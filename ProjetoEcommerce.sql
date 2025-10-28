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
	id INT PRIMARY KEY,
    cashback DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id) REFERENCES clientes(id)
);

CREATE TABLE vendedores(
	id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    causa_s VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    nota_m DECIMAL(10, 2) NOT NULL
);

CREATE TABLE produto (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(30) NOT NULL,
    descr VARCHAR(50) NOT NULL,
    qtd_e INT,
    valor DECIMAL(10, 2) NOT NULL,
    obs VARCHAR(35) NOT NULL,
	vendedor_id INT NOT NULL, 
    FOREIGN KEY (vendedor_id) REFERENCES vendedores(id)
);

