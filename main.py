from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

try: 
    conexao = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conexao.cursor()
    print("Conexão estabelecida com sucesso")

except mysql.connector.Error as err:
    print(f"Erro ao conectar: {err}")
    exit()


def executar_script_sql(arquivo):
    try:
        with open(arquivo, 'r') as file:
            sql_script = file.read()
        
        print(f"Executando comandos do arquivo: {arquivo}")

        for result in cursor.execute(sql_script, multi=True):
            if result.with_rows:
                pass
            elif result.rowcount > 0:
                print(f" -> {result.rowcount} linha(s) afetada(s) por um comando")
            else:
                print(f" -> Comando {result.statement.split()[0]} executado com sucesso")
        conexao.commit()
        print("Script SQL executado e alterações confirmadas com sucesso")

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado")
    except mysql.connector.Error as err:
        print(f"Erro de SQL durante a execução: {err}")
        conexao.rollback()

def cadastrarCliente():
    print("\n--- Cadastrar Cliente ---")

    from datetime import datetime
    
    nome = input("Digite o nome: ")
    idade = input("Digite a idade: ") 
    sexo = input("Digite o sexo: [m,f,o] ").lower()
    data_str = input("Digite a data de nascimento: [dd/mm/aaaa] ")

    try:
        data_n = datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        print("ERRO: Formato de data inválido. Use dd/mm/aaaa.")
        return 

    sql_query = "INSERT INTO clientes(nome, idade, sexo, data_n) VALUES (%s, %s, %s, %s)"
   
    dados = (nome, idade, sexo, data_n)
    
    try:
        cursor.execute(sql_query, dados)
        conexao.commit()
        print("Informações do cliente adicionadas com sucesso!")
    except mysql.connector.Error as err:
        print(f"Erro ao adicionar informações: {err}")
        conexao.rollback()


def cadastrarProduto():
    print("\n--- Cadastrar Produto ---")
    nome = input("Produto: ")
    descr = input("Descrição: ")

    try:
        qtd = int(input("Quantidade em estoque: "))
        valor = float(input("Valor: "))
    except ValueError:
        print("ERRO: Quantidade e Valor devem ser números válidos.")
        return

    obs = input("Obs: ")
    
    sql_query = "INSERT INTO produto(nome, descricao, quantidade_em_estoque, valor, observacoes) VALUES (%s, %s, %s, %s, %s)"
    dados = (nome, descr, qtd, valor, obs)
    
    try:
        cursor.execute(sql_query, dados)
        conexao.commit()
        print("Informações do produto adicionadas com sucesso!")
    except mysql.connector.Error as err:
        print(f"Erro ao adicionar informações: {err}")
        conexao.rollback()


def menu():
    while True:
        print("Sistema de E-commerce")
        print("1 - Criar Banco de dados")
        print("2 - Excluir Banco de dados")
        print("3. Cadastrar Novo Cliente ")
        print("4. Cadastrar Novo Produto ")
        print("5. Executar Estatísticas")
        print("0. Sair")

        resp = input("Escolha uma opção: ")

        if resp == '1':
            executar_script_sql("ProjetoEcommerce.sql")
        elif resp == '2':
            try:
                cursor.execute(f"DROP DATABASE IF EXISTS {database}")
                conexao.commit()
                print(f"Banco de dados '{database}' excluído com sucesso")
            except mysql.connector.Error as err:
                print(f"Erro ao excluir banco de dados: {err}")
        elif resp == '3':
            cadastrarCliente()
        elif resp == '4':
            cadastrarProduto()
        elif resp == '0':
            print("Encerrando o sistema. Até logo!")
            cursor.close()
            conexao.close()
            break
            
        else: 
            print("Opção inválida. Tente novamente.")
            
        
if __name__ == "__main__":
    menu()