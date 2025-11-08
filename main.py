from mysql.connector import Error
from dotenv import load_dotenv
import mysql.connector
import os
import getpass

load_dotenv()

class SistemaEcommerce:
    def __init__(self):
        self.conexao = None
        self.cursor = None
        self.usuario_atual = None
        self.tipo_usuario = None
    
    def tentar_conectar_com_usuario(self, username, senha):
        """Tenta conectar com um usuário específico e senha"""
        try:
            # Fecha conexão anterior se existir
            if self.conexao and self.conexao.is_connected():
                self.desconectar()
            
            self.conexao = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=username,
                password=senha,
                database=os.getenv("DB_NAME"),
                auth_plugin='mysql_native_password'
            )
            self.cursor = self.conexao.cursor(dictionary=True)
            self.usuario_atual = username
            self.definir_tipo_usuario(username)
            return True
        except Error as e:
            print(f"Falha na autenticação para {username}")
            return False
    
    def definir_tipo_usuario(self, username):
        """Define o tipo de usuário baseado no username"""
        if username == 'admin@localhost':
            self.tipo_usuario = 'admin'
        elif username == 'gerenteloja@localhost':
            self.tipo_usuario = 'gerente'
        elif username == 'funcionario@localhost':
            self.tipo_usuario = 'funcionario'
        else:
            self.tipo_usuario = 'desconhecido'
    
    def login(self):
        """Sistema de login pedindo para usuário digitar username e senha"""
        print("\n=== LOGIN SISTEMA E-COMMERCE ===")
        print("Usuários disponíveis: admin@localhost, gerenteloja@localhost, funcionario@localhost")
        
        tentativas = 0
        max_tentativas = 3
        
        while tentativas < max_tentativas:
            print(f"\nTentativa {tentativas + 1} de {max_tentativas}")
            
            username = input("Usuário: ").strip()
            senha = getpass.getpass("Senha: ")
            
            if self.tentar_conectar_com_usuario(username, senha):
                print(f"Login bem-sucedido! Bem-vindo, {username} ({self.tipo_usuario})")
                return True
            else:
                print("Usuário ou senha incorretos!")
                tentativas += 1
        
        print("Número máximo de tentativas excedido. Tente novamente mais tarde.")
        return False

    def verificar_privilegio(self, operacao, tabela=None):
        """Verifica se usuário tem privilégio para operação"""
        if self.tipo_usuario == 'admin':
            return True
        elif self.tipo_usuario == 'gerente':
            return operacao in ['SELECT', 'UPDATE', 'DELETE']
        elif self.tipo_usuario == 'funcionario':
            if operacao == 'SELECT':
                return True
            elif operacao == 'INSERT' and tabela == 'venda':
                return True
            return False
        return False

    def executar_procedure(self, nome_procedure, params=None):
        try:
            if params is None:
                params = []

            placeholders = ', '.join(['%s'] * len(params))
            query = f"CALL {nome_procedure}({placeholders})"
            
            self.cursor.execute(query, params)
            
            resultados = []
            for result in self.cursor.stored_results():
                resultados.extend(result.fetchall())
            
            self.conexao.commit()
            return True, resultados

        except Error as e:
            print(f"Erro ao executar procedure {nome_procedure}: {e}")
            if self.conexao and self.conexao.is_connected():
                self.conexao.rollback()
            return False, None

    def executar_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            else:
                self.conexao.commit()
                return None
        except Error as e:
            print(f"Erro ao executar query: {e}")
            return None

    def menu_clientes(self):
        if not self.verificar_privilegio('SELECT', 'cliente'):
            print("Você não tem permissão para gerenciar clientes")
            return
            
        while True:
            print("\nGERENCIAR CLIENTES")
            print("1. Adicionar cliente")
            print("2. Listar clientes (com idade calculada)") 
            print("3. Atualizar cliente")
            print("4. Deletar cliente")
            print("5. Clientes especiais")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                if not self.verificar_privilegio('INSERT', 'cliente'):
                    print("Sem permissão para adicionar clientes")
                    continue
                    
                nome = input("Nome: ").strip()
                sexo = input("Sexo (m/f/o): ").strip().lower()
                data_n = input("Data de nascimento (YYYY-MM-DD): ").strip()
                
                success, _ = self.executar_procedure("adicionar_cliente", [nome, 0, sexo, data_n])
                if success:
                    print("Cliente adicionado com sucesso. A idade será calculada automaticamente.")
                else:
                    print("Erro ao adicionar cliente.")
            
            elif opcao == "2":
                resultados = self.executar_query("""
                    SELECT id, nome, sexo, data_n, Calcula_idade(id) as idade 
                    FROM cliente
                """)
                if resultados:
                    print("\nLISTA DE CLIENTES (com idade calculada)")
                    for cliente in resultados:
                        print(f"ID: {cliente['id']} | Nome: {cliente['nome']} | Idade: {cliente['idade']} | Sexo: {cliente['sexo']} | Nascimento: {cliente['data_n']}")
                else:
                    print("Nenhum cliente encontrado")
            
            elif opcao == "3":
                if not self.verificar_privilegio('UPDATE', 'cliente'):
                    print("Sem permissão para atualizar clientes")
                    continue
                    
                try:
                    cliente_id = int(input("ID do cliente: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue
                novo_nome = input("Novo nome: ").strip()
                success, _ = self.executar_procedure("atualizar_cliente", [cliente_id, novo_nome])
                if success:
                    print("Cliente atualizado com sucesso.")
                else:
                    print("Erro ao atualizar cliente.")
            
            elif opcao == "4":
                if not self.verificar_privilegio('DELETE', 'cliente'):
                    print("Sem permissão para deletar clientes")
                    continue
                    
                try:
                    cliente_id = int(input("ID do cliente: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue
                success, _ = self.executar_procedure("deletar_cliente", [cliente_id])
                if success:
                    print("Cliente deletado com sucesso.")
                else:
                    print("Erro ao deletar cliente.")
            
            elif opcao == "5":
                resultados = self.executar_query("""
                    SELECT c.id, c.nome, Calcula_idade(c.id) as idade, ce.cashback 
                    FROM clientes_especiais ce 
                    JOIN cliente c ON ce.id_cliente = c.id
                """)
                if resultados:
                    print("\nCLIENTES ESPECIAIS")
                    for cliente in resultados:
                        print(f"ID: {cliente['id']} | Nome: {cliente['nome']} | Idade: {cliente['idade']} | Cashback: R${cliente['cashback']:.2f}")
                else:
                    print("Nenhum cliente especial encontrado")
            
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
    
    def menu_vendedores(self):
        if not self.verificar_privilegio('SELECT', 'vendedor'):
            print("Você não tem permissão para gerenciar vendedores")
            return
            
        while True:
            print("\nGERENCIAR VENDEDORES")
            print("1. Adicionar vendedor")
            print("2. Listar vendedores")
            print("3. Atualizar vendedor")
            print("4. Deletar vendedor")
            print("5. Vendedores com bonus")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                if not self.verificar_privilegio('INSERT', 'vendedor'):
                    print("Sem permissão para adicionar vendedores")
                    continue
                    
                nome = input("Nome: ").strip()
                causa_s = input("Causa/Especialidade: ").strip()
                tipo = input("Tipo (vendedor/gerente/CEO): ").strip().lower()
                try:
                    nota_media = float(input("Nota média (0.00-5.00): ").strip())
                except ValueError:
                    print("Nota média inválida. Use um número com ponto decimal.")
                    continue
                
                success, _ = self.executar_procedure("adicionar_vendedor", [nome, causa_s, tipo, nota_media])
                if success:
                    print("Vendedor adicionado com sucesso.")
                else:
                    print("Erro ao adicionar vendedor.")
            
            elif opcao == "2":
                resultados = self.executar_query("SELECT * FROM vendedor")
                if resultados:
                    print("\nLISTA DE VENDEDORES")
                    for vendedor in resultados:
                        print(f"ID: {vendedor['id']} | Nome: {vendedor['nome']} | Tipo: {vendedor['tipo']} | Nota: {vendedor['nota_media']} | Valor Vendido: R${vendedor['valor_vendido']:.2f}")
                else:
                    print("Nenhum vendedor encontrado.")
            
            elif opcao == "3":
                if not self.verificar_privilegio('UPDATE', 'vendedor'):
                    print("Sem permissão para atualizar vendedores")
                    continue
                    
                try:
                    vendedor_id = int(input("ID do vendedor: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue
                
                print("Deixe em branco para manter o valor atual:")
                novo_nome = input("Novo nome: ").strip()
                nova_causa = input("Nova causa/especialidade: ").strip()
                novo_tipo = input("Novo tipo (vendedor/gerente/CEO): ").strip().lower()
                nova_nota = input("Nova nota média: ").strip()
                
                vendedor_atual = self.executar_query("SELECT * FROM vendedor WHERE id = %s", (vendedor_id,))
                if not vendedor_atual:
                    print("Vendedor não encontrado.")
                    continue
                
                vendedor_atual = vendedor_atual[0]
                
                nome_final = novo_nome if novo_nome else vendedor_atual['nome']
                causa_final = nova_causa if nova_causa else vendedor_atual['causa_s']
                tipo_final = novo_tipo if novo_tipo else vendedor_atual['tipo']
                nota_final = float(nova_nota) if nova_nota else vendedor_atual['nota_media']
                
                success = self.executar_query(
                    "UPDATE vendedor SET nome = %s, causa_s = %s, tipo = %s, nota_media = %s WHERE id = %s",
                    (nome_final, causa_final, tipo_final, nota_final, vendedor_id)
                )
                
                if success is not None:
                    print("Vendedor atualizado com sucesso.")
                else:
                    print("Erro ao atualizar vendedor.")
            
            elif opcao == "4":
                if not self.verificar_privilegio('DELETE', 'vendedor'):
                    print("Sem permissão para deletar vendedores")
                    continue
                    
                try:
                    vendedor_id = int(input("ID do vendedor a ser deletado: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue
                
                produtos_associados = self.executar_query(
                    "SELECT COUNT(*) as total FROM produto WHERE id_vendedor = %s", 
                    (vendedor_id,)
                )
                
                if produtos_associados and produtos_associados[0]['total'] > 0:
                    print("Não é possível deletar este vendedor pois existem produtos associados a ele.")
                    print("Delete os produtos primeiro ou transfira-os para outro vendedor.")
                    continue
                
                confirmacao = input(f"Tem certeza que deseja deletar o vendedor ID {vendedor_id}? (s/N): ").strip().lower()
                if confirmacao == 's':
                    success = self.executar_query("DELETE FROM vendedor WHERE id = %s", (vendedor_id,))
                    if success is not None:
                        print("Vendedor deletado com sucesso.")
                    else:
                        print("Erro ao deletar vendedor.")
                else:
                    print("Operação cancelada.")
            
            elif opcao == "5":
                resultados = self.executar_query("""
                    SELECT v.id, v.nome, v.tipo, v.valor_vendido, fe.bonus 
                    FROM funcionario_especial fe 
                    JOIN vendedor v ON fe.id_vendedor = v.id
                """)
                if resultados:
                    print("\nVENDEDORES COM BÔNUS")
                    for vendedor in resultados:
                        print(f"ID: {vendedor['id']} | Nome: {vendedor['nome']} | Tipo: {vendedor['tipo']} | Valor Vendido: R${vendedor['valor_vendido']:.2f} | Bônus: R${vendedor['bonus']:.2f}")
                else:
                    print("Nenhum vendedor com bônus encontrado")
            
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
    
    def menu_produtos(self):
        if not self.verificar_privilegio('SELECT', 'produto'):
            print("Você não tem permissão para gerenciar produtos")
            return
            
        while True:
            print("\nGERENCIAR PRODUTOS")
            print("1. Adicionar produto")
            print("2. Listar produtos")
            print("3. Atualizar produto")
            print("4. Deletar produto")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                if not self.verificar_privilegio('INSERT', 'produto'):
                    print("Sem permissão para adicionar produtos")
                    continue
                    
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
                
                success, _ = self.executar_procedure("adicionar_produto", [nome, descr, qtd_estoque, valor, obs, id_vendedor])
                if success:
                    print("Produto adicionado com sucesso.")
                else:
                    print("Erro ao adicionar produto.")
            
            elif opcao == "2":
                resultados = self.executar_query("SELECT * FROM produto")
                if resultados:
                    print("\nLISTA DE PRODUTOS")
                    for produto in resultados:
                        print(f"ID: {produto['id']} | Nome: {produto['nome']} | Estoque: {produto['qtd_estoque']} | Valor: R${produto['valor']:.2f} | Vendedor ID: {produto['id_vendedor']}")
                else:
                    print("Nenhum produto encontrado.")
            
            elif opcao == "3":
                if not self.verificar_privilegio('UPDATE', 'produto'):
                    print("Sem permissão para atualizar produtos")
                    continue
                    
                try:
                    produto_id = int(input("ID do produto: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue
                
                produto_atual = self.executar_query("SELECT * FROM produto WHERE id = %s", (produto_id,))
                if not produto_atual:
                    print("Produto não encontrado.")
                    continue
                
                produto_atual = produto_atual[0]
                print(f"\nProduto atual: {produto_atual['nome']}")
                print("Deixe em branco para manter o valor atual:")
                
                novo_nome = input("Novo nome: ").strip()
                nova_descricao = input("Nova descrição: ").strip()
                novo_estoque = input("Nova quantidade em estoque: ").strip()
                novo_valor = input("Novo valor: ").strip()
                nova_obs = input("Nova observação: ").strip()
                novo_vendedor = input("Novo ID do vendedor: ").strip()
                
                nome_final = novo_nome if novo_nome else produto_atual['nome']
                descricao_final = nova_descricao if nova_descricao else produto_atual['descr']
                estoque_final = int(novo_estoque) if novo_estoque else produto_atual['qtd_estoque']
                valor_final = float(novo_valor) if novo_valor else produto_atual['valor']
                obs_final = nova_obs if nova_obs else produto_atual['obs']
                vendedor_final = int(novo_vendedor) if novo_vendedor else produto_atual['id_vendedor']
                
                success = self.executar_query(
                    "UPDATE produto SET nome = %s, descr = %s, qtd_estoque = %s, valor = %s, obs = %s, id_vendedor = %s WHERE id = %s",
                    (nome_final, descricao_final, estoque_final, valor_final, obs_final, vendedor_final, produto_id)
                )
                
                if success is not None:
                    print("Produto atualizado com sucesso.")
                else:
                    print("Erro ao atualizar produto.")
            
            elif opcao == "4":
                if not self.verificar_privilegio('DELETE', 'produto'):
                    print("Sem permissão para deletar produtos")
                    continue
                    
                try:
                    produto_id = int(input("ID do produto a ser deletado: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue
                
                vendas_associadas = self.executar_query(
                    "SELECT COUNT(*) as total FROM venda_produto WHERE id_produto = %s", 
                    (produto_id,)
                )
                
                if vendas_associadas and vendas_associadas[0]['total'] > 0:
                    print("Não é possível deletar este produto pois ele está associado a vendas.")
                    continue
                
                confirmacao = input(f"Tem certeza que deseja deletar o produto ID {produto_id}? (s/N): ").strip().lower()
                if confirmacao == 's':
                    success = self.executar_query("DELETE FROM produto WHERE id = %s", (produto_id,))
                    if success is not None:
                        print("Produto deletado com sucesso.")
                    else:
                        print("Erro ao deletar produto.")
                else:
                    print("Operação cancelada.")
            
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
                
    def menu_vendas(self):
        if not self.verificar_privilegio('SELECT', 'venda'):
            print("Você não tem permissão para gerenciar vendas")
            return
            
        while True:
            print("\nGERENCIAR VENDAS")
            print("1. Adicionar venda")
            print("2. Listar vendas")
            print("0. Voltar")

            opcao = input("Escolha: ").strip()

            if opcao == "1":
                if not self.verificar_privilegio('INSERT', 'venda'):
                    print("Sem permissão para adicionar vendas")
                    continue

                data_venda = input("Data da venda (YYYY-MM-DD): ").strip()
                hora = input("Hora (HH:MM:SS): ").strip()
                try:
                    id_cliente = int(input("ID do cliente: ").strip())
                    id_transp = int(input("ID da transportadora: ").strip())
                except ValueError:
                    print("ID inválido. Use apenas números.")
                    continue

                try:
                    query = "CALL adicionar_venda(%s, %s, %s, %s, @id_venda)"
                    self.cursor.execute(query, (data_venda, hora, id_cliente, id_transp))
                    
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
                        query = "CALL adicionar_produto_venda(%s, %s, %s, %s, %s, @mensagem)"
                        self.cursor.execute(query, (id_venda, id_produto_int, qtd, valor, obs))
                        
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
        if not self.verificar_privilegio('SELECT', 'transportadora'):
            print("Você não tem permissão para gerenciar transportadoras")
            return
            
        while True:
            print("\nGERENCIAR TRANSPORTADORAS")
            print("1. Adicionar transportadora")
            print("2. Listar transportadoras")
            print("3. Soma de fretes por cidade")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                if not self.verificar_privilegio('INSERT', 'transportadora'):
                    print("Sem permissão para adicionar transportadoras")
                    continue
                    
                nome = input("Nome: ").strip()
                cidade = input("Cidade: ").strip()
                transporte = input("Tipo de transporte: ").strip()
                
                success, _ = self.executar_procedure("adicionar_transportadora", [nome, cidade, transporte])
                if success:
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
            
            elif opcao == "3":
                cidade = input("Digite o nome da cidade para calcular fretes: ").strip()
                resultados = self.executar_query("SELECT Soma_fretes(%s) as total_fretes", (cidade,))
                
                if resultados and resultados[0] and 'total_fretes' in resultados[0]:
                    total = resultados[0]['total_fretes']
                    if total is not None and float(total) > 0:
                        print(f"Total de fretes para {cidade}: R${float(total):.2f}")
                    else:
                        print(f"Nenhum frete encontrado para a cidade {cidade}")
                else:
                    print(f"Nenhum frete encontrado para a cidade {cidade}")
            
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
    
    def menu_relatorios(self):
        while True:
            print("\nRELATÓRIOS")
            print("1. Estatísticas de vendas")
            print("2. Arrecadação por vendedor") 
            print("3. Total por vendedor (View)")
            print("4. Status do estoque (View)")
            print("5. Vendas detalhadas (View)")
            print("6. Soma de fretes por cidade")
            print("0. Voltar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                success, resultados = self.executar_procedure("EstatisticaVendas")
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
                        print(f"Total arrecadado pelo vendedor {vendedor_id} em {data}: R${float(total):.2f}")
                    else:
                        print("Nenhum valor encontrado para a data e vendedor informados.")
                else:
                    print("Nenhum valor encontrado para a data e vendedor informados.")
            
            elif opcao == "3":
                resultados = self.executar_query("SELECT * FROM total_por_vendedor")
                if resultados:
                    print("\nTOTAL POR VENDEDOR")
                    for vendedor in resultados:
                        print(f"Vendedor: {vendedor['nome_vendedor']} | Tipo: {vendedor['tipo_vendedor']} | Total Vendas: {vendedor['total_vendas_realizadas']} | Valor: R${vendedor['total_registrado']:.2f}")
                else:
                    print("Nenhum dado encontrado")
            
            elif opcao == "4":
                resultados = self.executar_query("SELECT * FROM status_estoque_vendedor")
                if resultados:
                    print("\nSTATUS DO ESTOQUE")
                    for produto in resultados:
                        print(f"Produto: {produto['nome_produto']} | Estoque: {produto['qtd_estoque']} | Status: {produto['status_estoque']} | Vendedor: {produto['nome_vendedor_resp']} | Tipo: {produto['tipo_vendedor']}")
                else:
                    print("Nenhum produto encontrado")
            
            elif opcao == "5":
                resultados = self.executar_query("SELECT * FROM vendas_detalhadas")
                if resultados:
                    print("\nVENDAS DETALHADAS")
                    for venda in resultados:
                        print(f"Venda: {venda['id_venda']} | Cliente: {venda['nome_cliente']} | Produto: {venda['nome_produto']} | Vendedor: {venda['vendedor_nome']} | Total: R${venda['total_venda']:.2f}")
                else:
                    print("Nenhuma venda encontrada")
            
            elif opcao == "6":
                cidade = input("Digite o nome da cidade para calcular fretes: ").strip()
                resultados = self.executar_query("SELECT Soma_fretes(%s) as total_fretes", (cidade,))
                
                if resultados and resultados[0] and 'total_fretes' in resultados[0]:
                    total = resultados[0]['total_fretes']
                    if total is not None and float(total) > 0:
                        print(f"Total de fretes para {cidade}: R${float(total):.2f}")
                    else:
                        print(f"Nenhum frete encontrado para a cidade {cidade}")
                else:
                    print(f"Nenhum frete encontrado para a cidade {cidade}")
            
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
    
    def menu_principal(self):
        while True:
            print(f"\nSISTEMA DE E-COMMERCE - Usuário: {self.usuario_atual} ({self.tipo_usuario})")
            print("1. Gerenciar Clientes")
            print("2. Gerenciar Vendedores") 
            print("3. Gerenciar Produtos")
            print("4. Gerenciar Vendas")
            print("5. Gerenciar Transportadoras")
            print("6. Relatórios")
            print("7. Trocar usuário")
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
            elif opcao == "7":
                self.desconectar()
                if not self.login():
                    print("Falha no login, saindo...")
                    break
            elif opcao == "0":
                print("Saindo...")
                break
            else:
                print("Opção inválida.")

    def desconectar(self):
        if self.conexao and self.conexao.is_connected():
            self.cursor.close()
            self.conexao.close()
            self.usuario_atual = None
            self.tipo_usuario = None
            print("Desconectado do banco de dados")

def main():
    sistema = SistemaEcommerce()
    
    if sistema.login():
        try:
            sistema.menu_principal()
        except KeyboardInterrupt:
            print("\nPrograma interrompido pelo usuário.")
        finally:
            sistema.desconectar()
    else:
        print("Não foi possível conectar ao banco de dados")

if __name__ == "__main__":
    main()