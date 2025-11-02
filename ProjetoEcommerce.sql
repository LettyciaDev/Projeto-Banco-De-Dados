CREATE DATABASE IF NOT EXISTS projeto;

USE projeto;

CREATE TABLE IF NOT EXISTS cliente(
	id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    idade TINYINT NOT NULL,
    sexo VARCHAR(1) CHECK(sexo = 'm' OR sexo = 'f' OR sexo = 'o') NOT NULL,
    data_n DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS vendedor(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    causa_s VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    cargo VARCHAR(20) CHECK(cargo = "vendedor" OR cargo = "gerente" OR cargo = "CEO"),
    nota_media DECIMAL(10, 2) NOT NULL,
    valor_vendido DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    salario DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS transportadora(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    cidade VARCHAR(50) NOT NULL,
    transporte VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS cliente_especial(
	id INT PRIMARY KEY,
    cashback DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id) REFERENCES cliente(id)
);

CREATE TABLE IF NOT EXISTS produto(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    descr VARCHAR(50) NOT NULL,
    qtd_e INT,
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
    id_produto INT NOT NULL,
    id_transp INT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id),
    FOREIGN KEY (id_produto) REFERENCES produto(id),
    FOREIGN KEY (id_transp) REFERENCES transportadora(id)
);

CREATE TABLE IF NOT EXISTS venda_produto(
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_venda INT NOT NULL,
    id_produto INT NOT NULL,
    qtd INT NOT NULL DEFAULT 1,
    valor DECIMAL(10, 2) NOT NULL,
    obs VARCHAR(35) NOT NULL,
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

DELIMITER //
CREATE FUNCTION Calcula_idade (cliente_id INT)
RETURNS INT DETERMINISTIC
BEGIN
    DECLARE data_nascimento DATE;
    DECLARE idade INT;

    SELECT data_n INTO data_nascimento
    FROM clientes
    WHERE id = cliente_id;

    SET idade = TIMESTAMPDIFF(YEAR, data_nascimento, CURDATE());

    RETURN idade;
END //
DELIMITER //

