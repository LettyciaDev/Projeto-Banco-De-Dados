from mysql.connector import Error
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

class SistemaEcommerce:
    def __init__(self):
        self.conexao = None
        self.cursor = None
    
    def conectar(self):
        try:
            self.conexao = mysql.connector.connect(
                host=host,
                user=user,    
                password=password,
                database=database
            )
            self.cursor = self.conexao.cursor(dictionary=True)
            print("Conectado ao banco de dados com sucesso")
            return True
        except Error as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def desconectar(self):
        if self.conexao and self.conexao.is_connected():
            self.cursor.close()
            self.conexao.close()
            print("Desconectado do banco de dados")

    def executar_procedure(self, nome_procedure, params=None):
        try:
            if params:
                self.cursor.callproc(nome_procedure, params)
            else:
                self.cursor.callproc(nome_procedure)
            
            resultados = []
            for resultado in self.cursor.fetchall():
                resultados.append(resultado)
            
            self.conexao.commit()
            
            while self.cursor.nextset():
                if self.cursor.description is not None:
                    for result in self.cursor.fetchall():
                        print(f"MENSAGEM DO BANCO: {result}")

            return resultados
        except Error as e:
            print(f"Erro ao executar procedure: {e}")
            if self.conexao and self.conexao.is_connected():
                self.conexao.rollback()
            return None 

    def executar_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao executar query: {e}")
            return None
    
    def menu_clientes(self):
        while True:
            print("\nGERENCIAR CLIENTES")
            print("1. Adicionar cliente")
            print("2. Listar clientes")
            print("3. Atualizar cliente")
            print("4. Deletar cliente")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                nome = input("Nome: ").strip()
                try:
                    idade = int(input("Idade: ").strip())
                except ValueError:
                    print("Idade inválida. Use apenas números.")
                    continue
                
                sexo = input("Sexo (m/f/o): ").strip().lower()
                data_n = input("Data de nascimento (YYYY-MM-DD): ").strip()
                
                self.executar_procedure("adicionar_cliente", [nome, idade, sexo, data_n])
                print("Cliente adicionado com sucesso.")
            
            elif opcao == "2":
                resultados = self.executar_query("SELECT * FROM cliente")
                if resultados:
                    print("\nLISTA DE CLIENTES")
                    for cliente in resultados:
                        print(f"ID: {cliente['id']} | Nome: {cliente['nome']} | Idade: {cliente['idade']} | Sexo: {cliente['sexo']} | Nascimento: {cliente['data_n']}")
                else:
                    print("Nenhum cliente encontrado")
            
            elif opcao == "3":
                cliente_id = input("ID do cliente: ").strip()
                novo_nome = input("Novo nome: ").strip()
                self.executar_procedure("atualizar_cliente", [cliente_id, novo_nome])
                print("Cliente atualizado com sucesso.")
            
            elif opcao == "4":
                cliente_id = input("ID do cliente: ").strip()
                self.executar_procedure("deletar_cliente", [cliente_id])
                print("Cliente deletado com sucesso.")
            
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
    
    def menu_vendedores(self):
        while True:
            print("\nGERENCIAR VENDEDORES")
            print("1. Adicionar vendedor")
            print("2. Listar vendedores")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                nome = input("Nome: ").strip()
                causa_s = input("Causa/Especialidade: ").strip()
                tipo = input("Tipo: ").strip()
                cargo = input("Cargo (vendedor/gerente/CEO): ").strip()
                try:
                    nota_media = float(input("Nota média (0.00-5.00): ").strip())
                except ValueError:
                    print("Nota média inválida. Use um número com ponto decimal.")
                    continue
                
                self.executar_procedure("adicionar_vendedor", [nome, causa_s, tipo, cargo, nota_media])
                print("Vendedor adicionado com sucesso.")
            
            elif opcao == "2":
                resultados = self.executar_query("SELECT * FROM vendedor")
                if resultados:
                    print("\nLISTA DE VENDEDORES")
                    for vendedor in resultados:
                        print(f"ID: {vendedor['id']} | Nome: {vendedor['nome']} | Cargo: {vendedor['cargo']} | Nota: {vendedor['nota_media']}")
                else:
                    print("Nenhum vendedor encontrado.")
            
            elif opcao == "0":
                break
            else:
                print("Opção invalida.")
    
    
    def menu_produtos(self):
        while True:
            print("\nGERENCIAR PRODUTOS")
            print("1. Adicionar produto")
            print("2. Listar produtos")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                nome = input("Nome: ").strip()
                descr = input("Descrição: ").strip()
                try:
                    qtd_estoque = int(input("Quantidade em estoque: ").strip())
                    valor = float(input("Valor: ").strip())
                except ValueError:
                    print("Quantidade ou Valor inválido. Use apenas números.")
                    continue

                obs = input("Observações: ").strip()
                id_vendedor = input("ID do vendedor: ").strip()
                
                self.executar_procedure("adicionar_produto", [nome, descr, qtd_estoque, valor, obs, id_vendedor])
                print("Produto adicionado com sucesso.")
            
            elif opcao == "2":
                resultados = self.executar_query("SELECT * FROM produto")
                if resultados:
                    print("\nLISTA DE PRODUTOS")
                    for produto in resultados:
                        print(f"ID: {produto['id']} | Nome: {produto['nome']} | Estoque: {produto['qtd_estoque']} | Valor: R${produto['valor']:.2f}")
                else:
                    print("Nenhum produto encontrado.")
            
            elif opcao == "0":
                break
            else:
                print("Opção invalida.")
                
    def menu_vendas(self):
        while True:
            print("\nGERENCIAR VENDAS")
            print("1. Adicionar venda")
            print("2. Listar vendas")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                data_venda = input("Data da venda (YYYY-MM-DD): ").strip()
                hora = input("Hora (HH:MM:SS): ").strip()
                id_cliente = input("ID do cliente: ").strip()
                id_transp = input("ID da transportadora: ").strip()
                
                resultados = self.executar_procedure("adicionar_venda", [data_venda, hora, id_cliente, id_transp, None])
                if resultados and len(resultados) > 0 and 'novo_id_venda' in resultados[0]:
                    id_venda = resultados[0]
                else:
                    print("Erro ao criar venda.")
                    
                while True:
                    id_produto = input("ID do produto (ou 0 para encerrar): ").strip().lower()
                    if id_produto == 0:
                        break
                    try:
                        qtd = int(input("Quantidadde: "))
                    except ValueError:
                        print("Quantidade inválida.")
                        continue
                    self.executar_procedure('adicionar_produto_venda', id_venda, id_produto, qtd)
                    print("Produto adicionado à venda com sucesso.")
                print("Venda registrada com sucesso.")

            elif opcao == "2":
                resultados = self.executar_query("SELECT * FROM vendas_detalhadas")
                if resultados:
                    print("\nVENDAS DETALHADAS")
                    for venda in resultados:
                        print(f"ID: {venda['id_venda']} | Cliente: {venda['nome_cliente']} | Produto: {venda['nome_produto']} | Total: R${venda['total_venda']:.2f}")
                else:
                    print("Nenhuma venda encontrada")
            
            elif opcao == "0":
                break
            else:
                print("Opção invalida.") 
    
    def menu_transportadoras(self):
        while True:
            print("\nGERENCIAR TRANSPORTADORAS")
            print("1. Adicionar transportadora")
            print("2. Listar transportadoras")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                nome = input("Nome: ").strip()
                cidade = input("Cidade: ").strip()
                transporte = input("Tipo de transporte: ").strip()
                
                self.executar_procedure("adicionar_transportadora", [nome, cidade, transporte])
                print("Transportadora adicionada com sucesso.")
            
            elif opcao == "2":
                resultados = self.executar_query("SELECT * FROM transportadora")
                if resultados:
                    print("\nLISTA DE TRANSPORTADORAS")
                    for transp in resultados:
                        print(f"ID: {transp['id']} | Nome: {transp['nome']} | Cidade: {transp['cidade']} | Transporte: {transp['transporte']}")
                else:
                    print("Nenhuma transportadora encontrada")
            
            elif opcao == "0":
                break
            else:
                print("Opção invalida.")
    
    def menu_relatorios(self):
        while True:
            print("\nRELATÓRIOS")
            print("1. Estatísticas de vendas")
            print("2. Arrecadação por vendedor")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                print("Gerando relatório...")
                self.executar_procedure("EstatisticaVendas")
            
            elif opcao == "2":
                vendedor_id = input("ID do vendedor: ").strip()
                data = input("Data (YYYY-MM-DD): ").strip()
                
                resultados = self.executar_query("SELECT Arrecadado(%s, %s) as total", (data, vendedor_id))
                
                if resultados and resultados[0] and 'total' in resultados[0]:
                    total = resultados[0]['total']
                    print(f"Total arrecadado: R${total:.2f}")
                else:
                    print("Nenhum valor encontrado para a data e vendedor informados.")
            
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
    
    def menu_principal(self):
        while True:
            print("\nSISTEMA DE GERENCIAMENTO DE VENDAS")
            print("1. Gerenciar Clientes")
            print("2. Gerenciar Vendedores")
            print("3. Gerenciar Produtos")
            print("4. Gerenciar Vendas")
            print("5. Gerenciar Transportadoras")
            print("6. Relatórios")
            print("0. Sair")
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.menu_clientes()
            elif opcao == "2":
                self.menu_vendedores()
            elif opcao == "3":
                self.menu_produtos()
            elif opcao == "4":
                self.menu_vendas()
            elif opcao == "5":
                self.menu_transportadoras()
            elif opcao == "6":
                self.menu_relatorios()
            elif opcao == "0":
                print("Saindo..")
                break
            else:
                print("Opção inválida.")

def main():
    sistema = SistemaEcommerce()
    if sistema.conectar():
        try:
            sistema.menu_principal()
        except KeyboardInterrupt:
            print("\nPrograma interrompido.")
        finally:
            sistema.desconectar()
    else:
        print("Não foi possível iniciar o sistema")
    
if __name__ == "__main__":
    main()