# 🏀 Sistema de E-commerce de Artigos de Esportes ⚽

Bem-vindo ao **Sistema de E-commerce de Artigos de Esportes**, um projeto desenvolvido para gerenciar uma loja virtual de produtos esportivos com funcionalidades completas e dinâmicas! Este sistema foi criado para a disciplina de **Projeto de Banco de Dados** do curso de **Ciência da Computação** da **Universidade Católica de Pernambuco**, sob orientação do professor **Jheymesson Apolinario Cavalcanti**. 🚀

---

## 🌟 Descrição do Projeto
Este é um sistema de e-commerce voltado para a venda de **artigos de esportes**, que gerencia **clientes**, **vendedores**, **produtos**, **transportadoras** e **vendas**. Ele inclui **triggers**, **procedures**, **functions** e **views** implementados em SQL para garantir eficiência e automação. 

---

## 💻 Equipe 
- **Anna Beatriz dos Santos Silva** 🏐 [`@Anninhaxs`](https://github.com/Anninhaxs)  
- **Bento Guilherme Gomes Oliveira** ⚽ [`@bnnto`](https://github.com/bnnto)  
- **João Victor Castelo Branco de Sena** 🏋️ [`@joao0cb`](https://github.com/joao0cb)  
- **Lettycia Vitoria Melo de França** 🏀 [`@LettyciaDev`](https://github.com/LettyciaDev)  

---

## 🗃️ Estrutura do Sistema

### 📋 Tabelas Principais
O sistema é estruturado com as seguintes tabelas:  
- **Cliente**: `id`, `nome`, `idade`, `sexo`, `data de nascimento`  
- **Cliente Especial**: Herda dados de `Cliente` + `cashback disponível`  
- **Vendedor** : `id`, `nome`, `causa social`, `tipo`, `nota média`  
- **Produto**: `id`, `nome`, `descrição`, `quantidade`, `valor`, `observações`  
- **Transportadora**: `id`, `nome`, `cidade`  
- **Venda**: `id`, `cliente`, `produto(s)`, `vendedor`, `transportadora`, `data e hora`, `valor total`  
- **Venda_Produto**: Herda dados de `Venda` e `Produto`, com `quantidade` e `observações`  

---

## ⚙️ Funcionalidades Implementadas

### 🛠️ Functions
1. **calcula_idade(id_cliente)**: Calcula a idade de um cliente com base na data de nascimento. 
2. **soma_fretes(destino)**: Soma os fretes para um destino específico. 
3. **arrecadado(data, id_vendedor)**: Calcula o total arrecadado por um vendedor em uma data. 

### 🔄 Triggers
1. **vendedor_bonus**: Aplica bônus automáticos para vendedores com base em vendas. 
2. **cashback_cliente**: Gerencia o cashback para clientes especiais.
3. **remove_cashback_zero**: Remove cashback zerado automaticamente. 

### 📜 Procedures
1. **reajuste(percentual, categoria)**: Ajusta preços de produtos por categoria (ex.: roupas, acessórios, equipamentos). 
2. **sorteio()**: Realiza sorteios para clientes ou promoções. 
3. **venda()**: Registra novas vendas no sistema. 
4. **estatisticas()**: Gera relatórios com estatísticas de vendas. 

### 📊 Views
- **vw_vendas_por_vendedor**: Exibe vendas agrupadas por vendedor. 
- **vw_clientes_especiais_cashback**: Lista clientes especiais com cashback disponível.  
- **vw_produtos_estoque_vendas**: Mostra produtos com estoque e histórico de vendas. 

---

## 👤 Usuários e Permissões
| Usuário          | Permissões Principais                              |
|-------------------|---------------------------------------------------|
| **Administrador**   | Acesso total ao sistema.                        |
| **Gerente**   | Buscar, editar e apagar registros.              |
| **Funcionário**  | Adicionar vendas e consultar informações.       |

---

## 🛠️ Ferramentas Utilizadas
- **Linguagem Principal**: Python  
- **Banco de Dados**: MySQL  
- **Bibliotecas**: `mysql.connector`  
- **Programas**: VS Code, MySQL Workbench 8.0 (Community)  

---

## 🚀 Como Executar
Siga os passos abaixo para rodar o sistema localmente:  

1. **Crie o banco de dados** no MySQL Workbench 8.0. 
2. **Baixe o arquivo** `ProjetoEcommerce.sql` e importe-o no MySQL. 
3. **Execute os scripts** para criar as tabelas, functions, triggers e procedures. 
4. **Crie um arquivo `.env`** com as seguintes variáveis:  
   ```sh
   DB_HOST=127.0.0.1
   DB_USER=root
   DB_PASSWORD=suasenha
   DB_NAME=projeto```
6. Rode o sistema principal `main.py`.
7. Use o menu para cadastrar clientes, produtos, vendedores e mais.
