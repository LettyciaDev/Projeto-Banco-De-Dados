# Sistema de E-commerce - Projeto Banco de Dados

### **Descrição**:

Este projeto implementa um **sistema de e-commerce de plantas**.  
O sistema gerencia **clientes, vendedores, produtos, transportadoras e vendas**, incluindo **triggers**, **procedures** e **functions** em SQL.

### **Equipe** 

- [`Anna Beatriz dos Santos Silva`](https://github.com/Anninhaxs)
- [`Bento Guilherme Gomes Oliveira`](https://github.com/bnnto) 
- [`João Victor Castelo Branco de Sena`](https://github.com/joao0cb) 
- [`Lettycia Vitoria Melo de França`](https://github.com/LettyciaDev)

Projeto desenvolvido para a disciplina de **Projeto de Banco de Dados** no curso de **Ciência da Computação** da **Universidade Católica de Pernambuco**, ministrada pelo professor Jheymesson Apolinario Cavalcanti.

---

## Estrutura do Sistema

### Tabelas Principais
- **Cliente:** id, nome, idade, sexo, data de nascimento  
- **Cliente Especial:** herda dados de cliente + cashback disponível  
- **Vendedor:** id, nome, causa social, tipo, nota média  
- **Produto:** id, nome, descrição, quantidade, valor, observações  
- **Transportadora:** id, nome, cidade  
- **Venda:** id, cliente, produto(s), vendedor, transportadora, data e hora, valor total
- **Venda_Produto:** herda dados de venda e produto, tem valor quantidade e obs

---

## Funcionalidades Implementadas

### Functions
1. **calcula_idade(id_cliente)**   
2. **soma_fretes(destino)**   
3. **arrecadado(data, id_vendedor)**

### Triggers
1. **vendedor_bonus**
2. **cashback_cliente**  
3. **remove_cashback_zero** 

### Procedures
1. **reajuste(percentual, categoria)**
2. **sorteio()**
3. **venda()**
4. **estatisticas()**

### Views
- `vw_vendas_por_vendedor`
- `vw_clientes_especiais_cashback`
- `vw_produtos_estoque_vendas`

### Usuários
| Usuário       | Permissões Principais |
|----------------|-----------------------|
| **Administrador** | Total |
| **Gerente**       | Buscar, editar, apagar registros |
| **Funcionário**   | Adicionar novas vendas, consultar |

---

## Ferramentas utilizadas

1. Linguagem principal: Python.
2. Banco de dados: MySQL.
3. Blibliotecas utilizadas: `mysql.connector`
4. Progamas usados: VS Code, MySQL Workbench 8.0 (Community).

---

## Como executar

1. Crie o banco de dados no MySQL Workbench 8.0.
2. Baixe e coloque o arquivo `ProjetoEcommerce.sql` no MySQL.
3. Execute os scripts.
4. Adicione um arquivo `.env` com essas informações:
```sh
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=suasenha
DB_NAME=projeto
```
6. Rode o sistema principal `main.py`.
7. Use o menu para cadastrar clientes, produtos, vendedores e mais.
