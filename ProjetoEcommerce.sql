CREATE DATABASE IF NOT EXISTS projeto;

USE projeto;

CREATE TABLE clientes(
	id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    idade TINYINT NOT NULL,
    sexo VARCHAR(1) CHECK(sexo = 'm' OR sexo = 'f' OR sexo = 'o') NOT NULL,
    data_n DATE NOT NULL
);

CREATE TABLE clientes_especiais(
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_cliente INT,
    cashback DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);

CREATE TABLE vendedores(
	id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    causa_s VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    cargo VARCHAR(10) CHECK(cargo = "vendedor" OR cargo = "gerente" OR cargo = "CEO"),
    nota_media DECIMAL(10, 2) NOT NULL,
    valor_vendido DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    salario DECIMAL(10, 2) NOT NULL DEFAULT 1000.00
);

CREATE TABLE funcionario_especial(
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_vendedor INT,
    bonus DECIMAL (10, 2) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_vendedor) REFERENCES vendedores(id)    
);

CREATE TABLE transportadora(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    cidade VARCHAR(50) NOT NULL,
    transporte VARCHAR(50) NOT NULL
);

CREATE TABLE produto (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    descr VARCHAR(50) NOT NULL,
    qtd_estoque INT,
    valor DECIMAL(10, 2) NOT NULL,
    obs VARCHAR(35) NOT NULL,
	vendedor_id INT NOT NULL, 
    FOREIGN KEY (vendedor_id) REFERENCES vendedores(id)
);

CREATE TABLE venda(
    id INT PRIMARY KEY AUTO_INCREMENT,
    data_venda DATE NOT NULL,
    hora TIME NOT NULL,
    id_cliente INT NOT NULL,
    id_produto INT NOT NULL,
    id_transp INT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    FOREIGN KEY (id_produto) REFERENCES produto(id),
    FOREIGN KEY (id_transp) REFERENCES transportadora(id)
);

CREATE TABLE venda_produto(
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_venda INT NOT NULL,
    id_produto INT NOT NULL,
    qtd INT NOT NULL DEFAULT 1,
    valor DECIMAL(10, 2) NOT NULL,
    obs VARCHAR(35) NOT NULL,
    FOREIGN KEY (id_venda) REFERENCES venda(id),
    FOREIGN KEY (id_produto) REFERENCES produto(id)
);

DELIMITER //
CREATE FUNCTION Calcula_idade (cliente_id INT)
RETURNS INT DETERMINISTIC
BEGIN
    DECLARE data_nascimento DATE;
    DECLARE idade INT;

    SELECT data_n INTO data_nascimento
    FROM clientes
    WHERE id = cliente_id

    SET idade = TIMESTAMDIFF(YEAR, data_nascimento, CURDATE());

    RETURN idade;

END //

DELIMITER;


DELIMITER //

-- Trigger de funcionario especial
DELIMITER $$
USE `projeto`$$
CREATE DEFINER = CURRENT_USER TRIGGER `projeto`.`vendedor_bonus` 
AFTER UPDATE ON `vendedores` 
FOR EACH ROW
BEGIN
	DECLARE bonus_total DECIMAL(10, 2);
    DECLARE bonus_vendedor DECIMAL(10, 2);
    
	IF NEW.valor_vendido > 1000 AND 
       (SELECT COUNT(*) FROM funcionario_especial WHERE id_vendedor = NEW.id) = 0 THEN
        
        SET bonus_vendedor = NEW.valor_vendido * 0.05;

        INSERT INTO funcionario_especial (id_vendedor, bonus)
        VALUES (NEW.id, bonus_vendedor);

        UPDATE vendedores
        SET salario = NEW.salario + bonus_vendedor
        WHERE id = NEW.id and id <> NEW.id;
    END IF;
    
    SELECT SUM(bonus) INTO bonus_total FROM funcionario_especial;
    
    SELECT CONCAT('Total de bônus salarial necessário para custear: R$ ', bonus_total) AS mensagem;
END$$
DELIMITER ;

-- Trigger de cliente especial
DELIMITER $$
USE `projeto`$$	
CREATE DEFINER = CURRENT_USER TRIGGER `projeto`.`cashback_cliente` 
AFTER INSERT ON `venda_produto` 
FOR EACH ROW
BEGIN
	DECLARE total_gasto DECIMAL(10,2);
    DECLARE cashback_cliente DECIMAL(10,2);
    DECLARE total_cashback DECIMAL(10,2);
		
    SELECT SUM(vendap.valor * vendap.qtd)
    INTO total_gasto
    FROM venda_produto vendap
    INNER JOIN venda v ON v.id = vendap.id_venda
    WHERE v.id_cliente = (
		SELECT v2.id_cliente FROM venda v2 WHERE v2.id = NEW.id_venda
	);
    
    IF total_gasto > 500 THEN 
		SET cashback_cliente = total_gasto * 0.02;
        
        IF NOT EXISTS (
			SELECT 1 FROM clientes_especiais ce
            INNER JOIN venda v ON v.id_cliente = ce.id_cliente
            WHERE v.id = NEW.id_venda
		) THEN
			INSERT INTO clientes_especiais (id_cliente, cashback)
			VALUES(
				(SELECT id_cliente FROM venda WHERE id = NEW.id_venda),
				cashback_cliente
			);
		ELSE
			UPDATE clientes_especiais ce
			INNER JOIN venda v ON v.id_cliente = ce.id_cliente
			SET ce.cashback = ce.cashback + cashback_cliente
			WHERE v.id = NEW.id_venda;
		END IF;
                
		SELECT SUM(cashback)
		INTO total_cashback
		FROM clientes_especiais;
                
		SELECT CONCAT('Total de cashback a ser custeado: R$ ', total_cashback) AS mensagem;
    END IF;            
END$$
DELIMITER ;