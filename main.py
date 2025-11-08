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
                database=database,
                auth_plugin='mysql_native_password'
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
            if params is None:
                params = []

            # Chama a procedure
            self.cursor.callproc(nome_procedure, params)

            # Captura resultados se houver
            resultados = []
            for result in self.cursor.stored_results():
                resultados.extend(result.fetchall())

            self.conexao.commit()

            # Para procedures com parâmetros OUT, precisamos fazer uma query separada
            # para obter os valores dos parâmetros
            if params:
                # Recupera os valores dos parâmetros (especialmente os OUT)
                out_params = []
                for i, param in enumerate(params):
                    if param == 0 or param is None:  # Parâmetro OUT
                        # Executa query para obter valor da variável de sessão
                        query = f"SELECT @_{nome_procedure}_{i}"
                        self.cursor.execute(query)
                        result = self.cursor.fetchone()
                        if result:
                            out_params.append(list(result.values())[0])
                        else:
                            out_params.append(None)
                    else:
                        out_params.append(param)
                
                return out_params, resultados
            else:
                return params, resultados

        except Error as e:
            print(f"Erro ao executar procedure {nome_procedure}: {e}")
            if self.conexao and self.conexao.is_connected():
                self.conexao.rollback()
            return None, None

    def executar_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # Verifica se é uma query que retorna resultados
            if query.strip().lower().startswith(('select', 'show', 'describe', 'call')):
                return self.cursor.fetchall()
            else:
                self.conexao.commit()
                return None
        except Error as e:
            print(f"Erro ao executar query: {e}")
            if self.conexao and self.conexao.is_connected():
                self.conexao.rollback()
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
                
                params, resultados = self.executar_procedure("adicionar_cliente", [nome, idade, sexo, data_n])
                if params is not None:
                    print("Cliente adicionado com sucesso.")
                else:
                    print("Erro ao adicionar cliente.")
            
            elif opcao == "2":
                resultados = self.executar_query("SELECT * FROM cliente")
                if resultados:
                    print("\nLISTA DE CLIENTES")
                    for cliente in resultados:
                        print(f"ID: {cliente['id']} | Nome: {cliente['nome']} | Idade: {cliente['idade']} | Sexo: {cliente['sexo']} | Nascimento: {cliente['data_n']}")
                else:
                    print("Nenhum cliente encontrado")
            
            elif opcao == "3":
                try:
                    cliente_id = int(input("ID do cliente: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue
                novo_nome = input("Novo nome: ").strip()
                params, resultados = self.executar_procedure("atualizar_cliente", [cliente_id, novo_nome])
                if params is not None:
                    print("Cliente atualizado com sucesso.")
                else:
                    print("Erro ao atualizar cliente.")
            
            elif opcao == "4":
                try:
                    cliente_id = int(input("ID do cliente: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue
                params, resultados = self.executar_procedure("deletar_cliente", [cliente_id])
                if params is not None:
                    print("Cliente deletado com sucesso.")
                else:
                    print("Erro ao deletar cliente.")
            
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
                
                params, resultados = self.executar_procedure("adicionar_vendedor", [nome, causa_s, tipo, cargo, nota_media])
                if params is not None:
                    print("Vendedor adicionado com sucesso.")
                else:
                    print("Erro ao adicionar vendedor.")
            
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
                print("Opção inválida.")
    
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
                try:
                    id_vendedor = int(input("ID do vendedor: ").strip())
                except ValueError:
                    print("ID do vendedor inválido. Use apenas números.")
                    continue
                
                params, resultados = self.executar_procedure("adicionar_produto", [nome, descr, qtd_estoque, valor, obs, id_vendedor])
                if params is not None:
                    print("Produto adicionado com sucesso.")
                else:
                    print("Erro ao adicionar produto.")
            
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
                print("Opção inválida.")
                
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
                try:
                    id_cliente = int(input("ID do cliente: ").strip())
                    id_transp = int(input("ID da transportadora: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue

                # Versão alternativa usando query direta para procedures com OUT
                try:
                    # Primeiro, criar a venda
                    query = "CALL adicionar_venda(%s, %s, %s, %s, @id_venda)"
                    self.cursor.execute(query, (data_venda, hora, id_cliente, id_transp))
                    
                    # Recuperar o ID da venda gerado
                    self.cursor.execute("SELECT @id_venda as id_venda")
                    result = self.cursor.fetchone()
                    
                    if result and 'id_venda' in result:
                        id_venda = result['id_venda']
                        print(f"Venda criada com sucesso! ID: {id_venda}")
                    else:
                        print("Erro ao criar venda: ID não retornado")
                        continue
                        
                except Error as e:
                    print(f"Erro ao criar venda: {e}")
                    continue

                # Adicionar produtos à venda
                while True:
                    id_produto = input("ID do produto (ou 0 para encerrar): ").strip()
                    if id_produto == "0":
                        break
                    try:
                        id_produto_int = int(id_produto)
                        qtd = int(input("Quantidade: "))
                        valor = float(input("Valor unitário: "))
                        obs = input("Observações: ").strip()
                    except ValueError:
                        print("Valor inválido.")
                        continue

                    try:
                        # Usando query direta para procedure com OUT
                        query = "CALL adicionar_produto_venda(%s, %s, %s, %s, %s, @mensagem)"
                        self.cursor.execute(query, (id_venda, id_produto_int, qtd, valor, obs))
                        
                        # Recuperar mensagem
                        self.cursor.execute("SELECT @mensagem as msg")
                        result = self.cursor.fetchone()
                        
                        if result and 'msg' in result:
                            print(result['msg'])
                        else:
                            print("Produto adicionado à venda.")
                            
                    except Error as e:
                        print(f"Erro ao adicionar produto: {e}")

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
                print("Opção inválida.") 
    
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
                
                params, resultados = self.executar_procedure("adicionar_transportadora", [nome, cidade, transporte])
                if params is not None:
                    print("Transportadora adicionada com sucesso.")
                else:
                    print("Erro ao adicionar transportadora.")
            
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
                print("Opção inválida.")
    
    def menu_relatorios(self):
        while True:
            print("\nRELATÓRIOS")
            print("1. Estatísticas de vendas")
            print("2. Arrecadação por vendedor")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                print("Gerando relatório...")
                params, resultados = self.executar_procedure("EstatisticaVendas")
                if resultados:
                    print("\nESTATÍSTICAS DE VENDAS:")
                    for resultado in resultados:
                        for key, value in resultado.items():
                            print(f"{key}: {value}")
                        print("-" * 30)
                else:
                    print("Nenhum dado encontrado para o relatório.")
            
            elif opcao == "2":
                try:
                    vendedor_id = int(input("ID do vendedor: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue
                data = input("Data (YYYY-MM-DD): ").strip()
                
                resultados = self.executar_query("SELECT Arrecadado(%s, %s) as total", (data, vendedor_id))
                
                if resultados and resultados[0] and 'total' in resultados[0]:
                    total = resultados[0]['total']
                    if total is not None:
                        print(f"Total arrecadado: R${float(total):.2f}")
                    else:
                        print("Nenhum valor encontrado para a data e vendedor informados.")
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
                print("Saindo...")
                break
            else:
                print("Opção inválida.")

def main():
    sistema = SistemaEcommerce()
    if sistema.conectar():
        try:
            sistema.menu_principal()
        except KeyboardInterrupt:
            print("\nPrograma interrompido pelo usuário.")
        finally:
            sistema.desconectar()
    else:
        print("Não foi possível iniciar o sistema devido a problemas de conexão.")
    
if __name__ == "__main__":
    main()