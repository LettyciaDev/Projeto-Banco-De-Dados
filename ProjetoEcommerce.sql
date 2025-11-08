CREATE DATABASE IF NOT EXISTS projeto;

USE projeto;

CREATE TABLE IF NOT EXISTS cliente(
	id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    idade TINYINT NOT NULL,
    sexo VARCHAR(1) NOT NULL CHECK(sexo = 'm' OR sexo = 'f' OR sexo = 'o'),
    data_n DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS vendedor(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    causa_s VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK(tipo = "vendedor" OR tipo = "gerente" OR tipo = "CEO"),
    nota_media DECIMAL(10, 2) NOT NULL CHECK (nota_media >= 0.00 AND nota_media <= 5.00),
    valor_vendido DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    salario DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS clientes_especiais(
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_cliente INT,
    cashback DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id)
);

CREATE TABLE IF NOT EXISTS funcionario_especial(
	id INT PRIMARY KEY AUTO_INCREMENT,
    id_vendedor INT,
    bonus DECIMAL (10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (id_vendedor) REFERENCES vendedor(id)    
);

CREATE TABLE IF NOT EXISTS transportadora(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    cidade VARCHAR(50) NOT NULL,
    transporte VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS produto(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    descr VARCHAR(50) NOT NULL,
    qtd_estoque INT,
    valor DECIMAL(10, 2) NOT NULL,
    obs VARCHAR(35) NOT NULL,
	id_vendedor INT NOT NULL, 
    FOREIGN KEY (id_vendedor) REFERENCES vendedor(id)
);

CREATE TABLE IF NOT EXISTS venda(
    id INT PRIMARY KEY AUTO_INCREMENT,
    data_venda DATE NOT NULL,
    hora TIME NOT NULL,
    id_cliente INT NOT NULL,
    id_transp INT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id),
    FOREIGN KEY (id_transp) REFERENCES transportadora(id)
);

CREATE TABLE IF NOT EXISTS venda_produto(
    id_venda INT NOT NULL,
    id_produto INT NOT NULL,
    qtd INT NOT NULL DEFAULT 1,
    valor DECIMAL(10, 2) NOT NULL,
    obs VARCHAR(35) NOT NULL,
    PRIMARY KEY(id_venda, id_produto),
    FOREIGN KEY (id_venda) REFERENCES venda(id),
    FOREIGN KEY (id_produto) REFERENCES produto(id)
);

CREATE USER IF NOT EXISTS 'admin@localhost' IDENTIFIED BY 'administrador20251102';
CREATE USER IF NOT EXISTS 'gerenteloja@localhost' IDENTIFIED BY 'gerentecargo123';
CREATE USER IF NOT EXISTS 'funcionario@localhost' IDENTIFIED BY 'funcionario543';

GRANT ALL PRIVILEGES ON projeto.* TO 'admin@localhost' WITH GRANT OPTION;
GRANT SELECT, DELETE, UPDATE ON projeto.* TO 'gerenteloja@localhost';
GRANT SELECT, INSERT ON projeto.venda TO 'funcionario@localhost';

FLUSH PRIVILEGES;

-- View vendas detalhadas
CREATE OR REPLACE VIEW vendas_detalhadas AS
SELECT venda.id AS id_venda,
cliente.nome AS nome_cliente,
produto.nome AS nome_produto,
vendedor.nome AS vendedor_nome,
venda.data_venda, venda.hora, venda_produto.qtd, venda_produto.valor,
(venda_produto.qtd * venda_produto.valor) AS total_venda
FROM venda
JOIN venda_produto ON venda_produto.id_venda = venda.id
JOIN produto ON venda_produto.id_produto = produto.id
JOIN vendedor ON produto.id_vendedor = vendedor.id
JOIN cliente ON venda.id_cliente = cliente.id;

-- View total por vendedor
CREATE OR REPLACE VIEW total_por_vendedor AS
SELECT vendedor.id AS id_vendedor,
vendedor.nome AS nome_vendedor,
vendedor.causa_s AS causa_social,
vendedor.tipo AS tipo_vendedor,
vendedor.nota_media AS nota_media,
vendedor.valor_vendido AS total_registrado,
COUNT(DISTINCT venda.id) AS total_vendas_realizadas
FROM vendedor
JOIN produto ON vendedor.id = produto.id_vendedor
JOIN venda_produto ON produto.id = venda_produto.id_produto
JOIN venda ON venda.id = venda_produto.id_venda
GROUP BY vendedor.id, vendedor.nome, vendedor.causa_s, vendedor.tipo, vendedor.nota_media, vendedor.valor_vendido;

-- View estoque do vendedor
CREATE OR REPLACE VIEW status_estoque_vendedor AS
SELECT
    P.nome AS nome_produto,
    P.descr AS descricao_produto,
    P.qtd_estoque,
    P.valor AS preco_unitario,
    P.obs AS observacao_produto,
    V.nome AS nome_vendedor_resp,
    V.cargo AS cargo_vendedor,
    CASE
        WHEN P.qtd_estoque > 50 THEN 'Estoque Alto'
        WHEN P.qtd_estoque BETWEEN 11 AND 50 THEN 'Estoque Moderado'
        WHEN P.qtd_estoque BETWEEN 1 AND 10 THEN 'Estoque Baixo'
        ELSE 'Esgotado'
    END AS status_estoque
FROM
    produto AS P
INNER JOIN
    vendedor AS V ON P.id_vendedor = V.id
ORDER BY
    P.qtd_estoque DESC, P.nome;
    
-- Função calcula_idade
DELIMITER //
CREATE FUNCTION Calcula_idade (cliente_id INT)
RETURNS INT DETERMINISTIC
BEGIN
    DECLARE data_nascimento DATE;
    DECLARE idade INT;

    SELECT data_n INTO data_nascimento
    FROM cliente
    WHERE id = cliente_id;

    SET idade = TIMESTAMPDIFF(YEAR, data_nascimento, CURDATE());

    RETURN idade;
END //
DELIMITER //

-- Função Soma_fretes
DELIMITER $$
CREATE FUNCTION Soma_fretes (destino VARCHAR(50))
RETURNS DECIMAL(10, 2)
READS SQL DATA
BEGIN
    DECLARE total_fretes DECIMAL(10, 2);

    SELECT
        SUM(VP.valor) INTO total_fretes
    FROM
        venda AS V
    INNER JOIN
        transportadora AS T ON V.id_transp = T.id
    INNER JOIN
        venda_produto AS VP ON V.id = VP.id_venda
    WHERE
        T.cidade = destino;

    RETURN IFNULL(total_fretes, 0.00);
END $$
DELIMITER ;

-- Função Arrecadado
DELIMITER $$
CREATE FUNCTION Arrecadado (data_venda DATE, id_vendedor_param INT)
RETURNS DECIMAL(10, 2)
READS SQL DATA
BEGIN
    DECLARE total_arrecadado DECIMAL(10, 2);

    SELECT
        SUM(VP.valor) INTO total_arrecadado
    FROM
        venda AS V
    INNER JOIN
        venda_produto AS VP ON V.id = VP.id_venda
    INNER JOIN
        produto AS P ON VP.id_produto = P.id
    WHERE
        V.data_venda = data_venda AND P.id_vendedor = id_vendedor_param;

    RETURN IFNULL(total_arrecadado, 0.00);
END $$
DELIMITER ;

-- Trigger de funcionario especial
DELIMITER $$
CREATE TRIGGER vendedor_bonus 
AFTER UPDATE ON vendedor 
FOR EACH ROW
BEGIN
	DECLARE bonus_total DECIMAL(10, 2);
    DECLARE bonus_vendedor DECIMAL(10, 2);
    
	IF NEW.valor_vendido > 1000 AND 
       (SELECT COUNT(*) FROM funcionario_especial WHERE id_vendedor = NEW.id) = 0 THEN
        
        SET bonus_vendedor = NEW.valor_vendido * 0.05;

        INSERT INTO funcionario_especial (id_vendedor, bonus)
        VALUES (NEW.id, bonus_vendedor);

        UPDATE vendedor
        SET salario = NEW.salario + bonus_vendedor
        WHERE id = NEW.id;
    END IF;
    
    SELECT SUM(bonus) INTO bonus_total FROM funcionario_especial;
END$$
DELIMITER ;
	
-- Trigger de cliente especial
DELIMITER $$
CREATE TRIGGER cashback_cliente 
AFTER INSERT ON venda_produto 
FOR EACH ROW
BEGIN
	DECLARE total_gasto DECIMAL(10,2);
    DECLARE cashback_cliente DECIMAL(10,2);
    DECLARE total_cashback DECIMAL(10,2);
	DECLARE cliente_id INT;
    
    SELECT id_cliente INTO cliente_id
	FROM venda
    WHERE id = NEW.id_venda;
    
    SELECT SUM(vendap.valor * vendap.qtd)
    INTO total_gasto
    FROM venda_produto vendap
    INNER JOIN venda v ON v.id = vendap.id_venda
    WHERE v.id_cliente = cliente_id;
    
    IF total_gasto > 500 THEN 
		SET cashback_cliente = total_gasto * 0.02;
        
        IF NOT EXISTS (
			SELECT 1 FROM clientes_especiais ce
            WHERE ce.id_cliente = cliente_id
		) THEN
			INSERT INTO clientes_especiais (id_cliente, cashback)
			VALUES(cliente_id, cashback_cliente);
		ELSE
			UPDATE clientes_especiais
			SET cashback = cashback + cashback_cliente
            WHERE id_cliente = cliente_id;
		END IF;
        
		SELECT SUM(cashback)
		INTO total_cashback
		FROM clientes_especiais;
    END IF;            
END$$
DELIMITER ;

-- trigger para tirar cliente especial
DELIMITER $$
CREATE TRIGGER remover_cliente_especial
AFTER UPDATE ON clientes_especiais
FOR EACH ROW
BEGIN
	IF NEW.cashback = 0 THEN
		DELETE FROM clientes_especiais
        WHERE id_cliente = NEW.id_cliente;
	END IF;
END$$
DELIMITER ;

-- procedimento de reajuste salario
DELIMITER $$ 
CREATE PROCEDURE reajuste_salario (
	IN p_percentual DECIMAL(5, 2),
    IN p_tipo VARCHAR(20)
)
BEGIN
	UPDATE vendedor
    SET salario = salario + (salario * (p_percentual / 100))
    WHERE tipo = p_tipo;
END$$
DELIMITER ;

-- procedimento de sorteio 
DELIMITER $$

CREATE PROCEDURE sortear_cliente_premiado()
BEGIN
    DECLARE v_id_cliente INT;
    DECLARE v_nome_cliente VARCHAR(50);
    DECLARE v_valor_voucher DECIMAL(10,2);
    DECLARE v_especial INT DEFAULT 0;

    -- Sortear um cliente aleatoriamente
    SELECT id, nome
    INTO v_id_cliente, v_nome_cliente
    FROM cliente
    ORDER BY RAND()
    LIMIT 1;

    -- Verificar se o cliente está na tabela de clientes especiais
    SELECT COUNT(*) INTO v_especial
    FROM clientes_especiais
    WHERE id_cliente = v_id_cliente;

    -- Definir valor do voucher conforme o tipo de cliente
    IF v_especial > 0 THEN
        SET v_valor_voucher = 200.00;
    ELSE
        SET v_valor_voucher = 100.00;
    END IF;

    -- Exibir o resultado do sorteio
    SELECT 
        v_id_cliente AS id_cliente_sorteado,
        v_nome_cliente AS nome_cliente,
        IF(v_especial > 0, 'Cliente Especial', 'Cliente Comum') AS tipo_cliente,
        v_valor_voucher AS valor_voucher,
        CONCAT('Parabéns, ', v_nome_cliente, '! Você ganhou um voucher de R$ ', FORMAT(v_valor_voucher, 2), '!') AS mensagem;
END$$

DELIMITER ;

-- procedimento de estatisticas
DELIMITER $$
CREATE PROCEDURE EstatisticaVendas()
BEGIN
	DECLARE produto_mais_vendido INT;
    DECLARE produto_menos_vendido INT;
    DECLARE vendedor_associado INT;
    DECLARE nome_vendedor VARCHAR(50);
    DECLARE nome_produto_mais VARCHAR(50);
    DECLARE nome_produto_menos VARCHAR(50);
    DECLARE valor_mais_vendido DECIMAL(10,2);
    DECLARE valor_menos_vendido DECIMAL(10,2);
    DECLARE mes_maior_venda_mais INT;
    DECLARE mes_menor_venda_mais INT;
    DECLARE mes_maior_venda_menos INT;
    DECLARE mes_menor_venda_menos INT;
    
    SELECT id_produto
    INTO produto_mais_vendido
    FROM venda_produto
    GROUP BY id_produto
    ORDER BY SUM(qtd) DESC
    LIMIT 1;
    
    SELECT id_produto
    INTO produto_menos_vendido
    FROM venda_produto
    GROUP BY id_produto
    ORDER BY SUM(qtd) ASC
    LIMIT 1;
    
    SELECT nome INTO nome_produto_mais FROM produto WHERE id = produto_mais_vendido;
    SELECT nome INTO nome_produto_menos FROM produto WHERE id = produto_menos_vendido;
    
    SELECT id_vendedor INTO vendedor_associado FROM produto WHERE id = produto_mais_vendido;
    SELECT nome INTO nome_vendedor FROM vendedor WHERE id = vendedor_associado;
    
    SELECT SUM(vp.qtd * vp.valor)
    INTO valor_mais_vendido
    FROM venda_produto vp
    WHERE vp.id_produto = produto_mais_vendido;
    
    SELECT SUM(vp.qtd * vp.valor)
    INTO valor_menos_vendido
    FROM venda_produto vp
    WHERE vp.id_produto = produto_menos_vendido;	
    
    SELECT MONTH(v.data_venda)
    INTO mes_maior_venda_mais
    FROM venda v
    JOIN venda_produto vp ON vp.id_venda = v.id
    WHERE vp.id_produto = produto_mais_vendido
    GROUP BY MONTH(v.data_venda)
    ORDER BY SUM(vp.qtd) DESC
    LIMIT 1;
    
    SELECT MONTH(v.data_venda)
    INTO mes_menor_venda_mais
    FROM venda v
    JOIN venda_produto vp ON vp.id_venda = v.id
    WHERE vp.id_produto = produto_mais_vendido
    GROUP BY MONTH(v.data_venda)
    ORDER BY SUM(vp.qtd) ASC
    LIMIT 1;
    
    SELECT MONTH(v.data_venda)
    INTO mes_maior_venda_menos
    FROM venda v
    JOIN venda_produto vp ON vp.id_venda = v.id
    WHERE vp.id_produto = produto_menos_vendido
    GROUP BY MONTH(v.data_venda)
    ORDER BY SUM(vp.qtd) DESC
    LIMIT 1;
    
    SELECT MONTH(v.data_venda)
    INTO mes_menor_venda_menos
    FROM venda v
    JOIN venda_produto vp ON vp.id_venda = v.id
    WHERE vp.id_produto = produto_menos_vendido
    GROUP BY MONTH(v.data_venda)
    ORDER BY SUM(vp.qtd) ASC
    LIMIT 1;
    
    SELECT 
        CONCAT('Produto mais vendido: ', nome_produto_mais) AS info1,
        CONCAT('Vendedor associado: ', nome_vendedor) AS info2,
        CONCAT('Valor ganho com o produto mais vendido: R$ ', FORMAT(valor_mais_vendido, 2)) AS info3,
        CONCAT('Mês de maior venda (produto mais vendido): ', mes_maior_venda_mais) AS info4,
        CONCAT('Mês de menor venda (produto mais vendido): ', mes_menor_venda_mais) AS info5,
        CONCAT('Produto menos vendido: ', nome_produto_menos) AS info6,
        CONCAT('Valor ganho com o produto menos vendido: R$ ', FORMAT(valor_menos_vendido, 2)) AS info7,
        CONCAT('Mês de maior venda (produto menos vendido): ', mes_maior_venda_menos) AS info8,
        CONCAT('Mês de menor venda (produto menos vendido): ', mes_menor_venda_menos) AS info9;
END$$
DELIMITER ;

DELIMITER $$

-- atualizar_estoque: OUT p_msg
DROP PROCEDURE IF EXISTS atualizar_estoque $$
CREATE PROCEDURE atualizar_estoque(
    IN p_id_produto INT,
    IN p_qtd_vendida INT,
    OUT p_msg VARCHAR(100)
)
BEGIN
    DECLARE estoque_atual INT;
    START TRANSACTION;

    SELECT qtd_estoque INTO estoque_atual
    FROM produto
    WHERE id = p_id_produto
    FOR UPDATE;

    IF estoque_atual IS NULL THEN
        SET p_msg = 'Produto não encontrado.';
        ROLLBACK;
    ELSEIF estoque_atual <= 0 THEN
        SET p_msg = 'Estoque do produto está vazio.';
        ROLLBACK;
    ELSEIF estoque_atual < p_qtd_vendida THEN
        SET p_msg = 'Estoque insuficiente.';
        ROLLBACK;
    ELSE
        UPDATE produto
        SET qtd_estoque = qtd_estoque - p_qtd_vendida
        WHERE id = p_id_produto;
        COMMIT;
        SET p_msg = 'Estoque atualizado com sucesso.';
    END IF;
END $$
 
-- adicionar_venda com OUT p_novo_id_venda
DROP PROCEDURE IF EXISTS adicionar_venda $$
CREATE PROCEDURE adicionar_venda(
    IN p_data_venda DATE,
    IN p_hora TIME,
    IN p_id_cliente INT,
    IN p_id_transp INT,
    OUT p_novo_id_venda INT
)
BEGIN
    START TRANSACTION;
    INSERT INTO venda (data_venda, hora, id_cliente, id_transp)
      VALUES (p_data_venda, p_hora, p_id_cliente, p_id_transp);
    SET p_novo_id_venda = LAST_INSERT_ID();
    COMMIT;
END $$

-- adicionar_produto_venda usa OUT p_msg (nome correto)
DROP PROCEDURE IF EXISTS adicionar_produto_venda $$
CREATE PROCEDURE adicionar_produto_venda(
    IN p_id_venda INT,
    IN p_id_produto INT,
    IN p_qtd INT,
    IN p_valor DECIMAL(10,2),
    IN p_obs VARCHAR(50),
    OUT p_msg VARCHAR(200)
)
BEGIN
    DECLARE v_msg_estoque VARCHAR(100);
    START TRANSACTION;

    INSERT INTO venda_produto (id_venda, id_produto, qtd, valor, obs)
    VALUES (p_id_venda, p_id_produto, p_qtd, p_valor, p_obs);

    CALL atualizar_estoque(p_id_produto, p_qtd, v_msg_estoque);

    IF v_msg_estoque != 'Estoque atualizado com sucesso.' THEN
        ROLLBACK;
        SET p_msg = CONCAT('Erro ao adicionar produto: ', v_msg_estoque);
    ELSE
        COMMIT;
        SET p_msg = 'Produto adicionado a venda e estoque atualizado.';
    END IF;
END $$

DELIMITER ;
--

DELIMITER $$
CREATE PROCEDURE adicionar_cliente(
	IN p_nome VARCHAR(30),
    IN p_idade TINYINT,
    IN p_sexo VARCHAR(1),
    IN p_data_n DATE
)
BEGIN
	INSERT INTO cliente (nome, idade, sexo, data_n)
    VALUES(p_nome, p_idade, p_sexo, p_data_n);
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE atualizar_cliente(
	IN p_id INT,
    IN p_novo_nome VARCHAR(30)
)
BEGIN
	UPDATE cliente SET nome = p_novo_nome WHERE id = p_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE deletar_cliente(IN p_id INT)
BEGIN
	DELETE FROM cliente WHERE id = p_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE adicionar_vendedor(
	IN p_nome VARCHAR(30),
    IN p_causa_s VARCHAR(50),
    IN p_tipo VARCHAR(20),
    IN p_cargo VARCHAR(20),
    IN p_nota_media DECIMAL(10, 2)
)
BEGIN
    INSERT INTO vendedor (nome, causa_s, tipo, cargo, nota_media) 
    VALUES (p_nome, p_causa_s, p_tipo, p_cargo, p_nota_media);
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE adicionar_produto(
    IN p_nome VARCHAR(30),
    IN p_descr VARCHAR(50),
    IN p_qtd_estoque INT,
    IN p_valor DECIMAL(10, 2),
    IN p_obs VARCHAR(35),
    IN p_id_vendedor INT
)
BEGIN
    INSERT INTO produto (nome, descr, qtd_estoque, valor, obs, id_vendedor) 
    VALUES (p_nome, p_descr, p_qtd_estoque, p_valor, p_obs, p_id_vendedor);
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE adicionar_transportadora(
    IN p_nome VARCHAR(50),
    IN p_cidade VARCHAR(50),
    IN p_transporte VARCHAR(50)
)
BEGIN
    INSERT INTO transportadora (nome, cidade, transporte) 
    VALUES (p_nome, p_cidade, p_transporte);
END$$
DELIMITER ;