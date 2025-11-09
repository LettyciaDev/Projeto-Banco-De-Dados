# Sistema de E-commerce de Artigos de Esportes

Bem-vindo ao **Sistema de E-commerce de Artigos de Esportes**, um projeto desenvolvido para gerenciar uma loja virtual de produtos esportivos com funcionalidades completas e dinâmicas! Este sistema foi criado para a disciplina de **Projeto de Banco de Dados** do curso de **Ciência da Computação** da **Universidade Católica de Pernambuco**, ministrada pelo professor **Jheymesson Apolinario Cavalcanti**.

---

## Descrição
Este é um sistema de e-commerce voltado para a venda de **artigos de esportes**, que gerencia **clientes**, **vendedores**, **produtos**, **transportadoras** e **vendas**. Ele inclui **triggers**, **procedures**, **functions** e **views** implementados em MySQL. 

---

## Equipe 
- **Anna Beatriz dos Santos Silva** [`@Anninhaxs`](https://github.com/Anninhaxs)  
- **Bento Guilherme Gomes Oliveira**  [`@bnnto`](https://github.com/bnnto)  
- **João Victor Castelo Branco de Sena** [`@joao0cb`](https://github.com/joao0cb)  
- **Lettycia Vitoria Melo de França** [`@LettyciaDev`](https://github.com/LettyciaDev)  

---

## Estrutura do Sistema

### Tabelas Principais

- **Cliente**: `id`, `nome`, `idade`, `sexo`, `data de nascimento`  
- **Cliente Especial**: Herda dados de `Cliente` + `cashback disponível`  
- **Vendedor** : `id`, `nome`, `causa social`, `tipo`, `nota média`  
- **Produto**: `id`, `nome`, `descrição`, `quantidade`, `valor`, `observações`  
- **Transportadora**: `id`, `nome`, `cidade`  
- **Venda**: `id`, `cliente`, `produto(s)`, `vendedor`, `transportadora`, `data e hora`, `valor total`  
- **Venda_Produto**: Popular os produtos de uma `venda`, para que seja possível que uma venda tenha vários `produtos` 

### Modelos do Banco de Dados  
- **Modelo Conceitual**:
    
  ![Modelo Conceitual](/assets/modelo_conceitual.png)  
- **Modelo Lógico**:
  
  ![Modelo Lógico](/assets/modelo_logico.png)
---

## Funcionalidades Implementadas

### Functions
1. `calcula_idade(id_cliente)`: Calcula a idade de um cliente com base na data de nascimento. 
2. `soma_fretes(destino)`: Soma os fretes para um destino específico. 
3. `arrecadado(data, id_vendedor)`: Calcula o total arrecadado por um vendedor em uma data. 

### Triggers
1. `vendedor_bonus`: Se funcionario vender mais de 1000 reais ele vira funcionário especial e ganha bonus no salário.
2. `cashback_cliente`: Cliente entra na tabela clientes especiais e ganha cashback.
3. `remove_cliente_especial`: Remove cliente da tabela de clientes especiais se o cashback for = 0. 

### Procedures
1. `reajuste(percentual, categoria)`: Ajusta preços de produtos por categoria (ex.: roupas, acessórios, equipamentos). 
2. `sorteio()` Realiza sorteios para clientes ou promoções. 
3. `venda()`: Registra novas vendas no sistema. 
4. `estatisticas()`: Gera relatórios com estatísticas de vendas. 

### Views
- `vw_vendas_por_vendedor`: Exibe vendas agrupadas por vendedor. 
- `vw_clientes_especiais_cashback`: Lista clientes especiais com cashback disponível.  
- `vw_produtos_estoque_vendas`: Mostra produtos com estoque e histórico de vendas. 

---

## Usuários e Permissões
| Usuário          | Permissões Principais                              |
|-------------------|---------------------------------------------------|
| **Administrador**   | Acesso total.                        |
| **Gerente**   | Buscar, editar e apagar registros.              |
| **Funcionário**  | Adicionar vendas e consultar informações.       |

---

## Ferramentas Utilizadas
- **Linguagem Principal**: Python  
- **Banco de Dados**: MySQL  
- **Bibliotecas**: `mysql.connector`  
- **Programas**: VS Code, MySQL Workbench 8.0 (Community)  

---

## Como Executar

1. **Crie o banco de dados** no MySQL Workbench 8.0. 
2. **Baixe o arquivo** `ProjetoEcommerce.sql` e coloque no MySQL. 
3. **Execute os scripts** para criar as tabelas, functions, triggers e procedures. 
4. **Crie um arquivo `.env`** com as seguintes variáveis:
    
   ```
   DB_HOST=127.0.0.1
   DB_USER=root
   DB_PASSWORD=suasenha
   DB_NAME=projeto
   ```
6. Rode o sistema principal `main.py`.
7. Use o menu para cadastrar clientes, produtos, vendedores e mais.
