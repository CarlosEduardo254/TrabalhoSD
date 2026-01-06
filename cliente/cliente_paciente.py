import requests
import sys
import threading
import pika

# Configurações de conexão
API_USUARIOS = "http://localhost:8083"
API_AGENDAMENTO = "http://localhost:8081"

# Flag para controlar a thread
thread_notificacao_ativa = True

def receber_notificacoes():
    """Thread que escuta notificações do RabbitMQ em tempo real"""
    global thread_notificacao_ativa
    
    while thread_notificacao_ativa:
        try:
            # Conexão com o RabbitMQ
            credentials = pika.PlainCredentials('user', 'password')
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
            )
            channel = connection.channel()
            
            # Declara a fila (usa a mesma que o worker ou uma específica)
            channel.queue_declare(queue='notificacao_cliente_queue')
            
            # Função callback chamada quando uma mensagem chega
            def callback(ch, method, properties, body):
                mensagem = body.decode('utf-8')
                print(f"\n\n{'='*50}")
                print(f"🔔 NOVA NOTIFICAÇÃO: {mensagem}")
                print(f"{'='*50}\n")
            
            # Configura o consumidor
            channel.basic_consume(
                queue='notificacao_cliente_queue', 
                on_message_callback=callback, 
                auto_ack=True
            )
            
            print("[Sistema] Escuta de notificações ativada...")
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError:
            print("[Sistema] RabbitMQ não disponível, tentando reconectar em 5s...")
            import time
            time.sleep(5)
        except Exception as e:
            print(f"[Sistema] Erro na escuta de notificações: {e}")
            import time
            time.sleep(5)

def menu_principal():
    # Inicia a thread de notificações em background
    thread_notificacao = threading.Thread(target=receber_notificacoes, daemon=True)
    thread_notificacao.start()
    
    while True:
        print("\n=== SYSTEM HOSPITALAR: PACIENTE ===")
        print("1. Cadastrar")
        print("2. Login")
        print("0. Sair")
        opcao = input("Opção: ")

        if opcao == '1':
            cadastrar_paciente()
        elif opcao == '2':
            fazer_login()
        elif opcao == '0':
            global thread_notificacao_ativa
            thread_notificacao_ativa = False
            sys.exit()
        else:
            print("Opção inválida.")

def cadastrar_paciente():
    print("\n--- Cadastro de Paciente ---")
    nome = input("Nome Completo: ")
    email = input("E-mail: ")
    senha = input("Senha: ")
    telefone = input("Telefone: ")
    problema = input("Problema/Sintoma: ")
    
    payload = {
        "tipo": "paciente",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone,
        "info_extra": problema
    }
    
    try:
        resp = requests.post(f"{API_USUARIOS}/criar_usuario", json=payload)
        if resp.status_code == 200:
            dados = resp.json()
            if dados.get('id') != 0:
                print(f"Sucesso! ID Gerado: {dados.get('id')}")
            else:
                print(f"Falha ao Cadastrar: {dados.get('mensagem')}")
        else:
            print(f"Erro: {resp.json()}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

def fazer_login():
    print("\n--- Login ---")
    email = input("E-mail: ")
    senha = input("Senha: ")
    
    payload = {"email": email, "senha": senha}
    
    try:
        resp = requests.post(f"{API_USUARIOS}/login", json=payload)
        if resp.status_code == 200:
            dados = resp.json()
            if dados.get("perfil") == "paciente":
                menu_area_logada(dados)
            else:
                print("Login Negado: Este painel é apenas para PACIENTES.")
        else:
            print(f"Login falhou: {resp.json()}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

def menu_area_logada(dados_usuario):
    print(f"\nBem-vindo, {dados_usuario['nome']}!")
    id_paciente = dados_usuario['id']
    
    while True:
        print("\n--- Menu Paciente ---")
        print("1. Agendar Consulta")
        print("2. Atualizar Dados Cadastrais")
        print("3. Ver Minhas Consultas")
        print("4. Cancelar Consulta")
        print("5. Pagar Consulta Pendente")
        print("6. Excluir Conta")
        print("0. Logout")
        
        opcao = input("Opção: ")
        
        if opcao == '1':
            agendar(id_paciente)
        elif opcao == '2':
            atualizar_dados(id_paciente)
        elif opcao == '3':
            ver_minhas_consultas(id_paciente)
        elif opcao == '4':
            cancelar_consulta(id_paciente)
        elif opcao == '5':
            pagar_consulta(id_paciente)
        elif opcao == '6':
            if excluir_conta(id_paciente):
                return
        elif opcao == '0':
            return
        else:
            print("Opção inválida.")

def atualizar_dados(id_paciente):
    print("\n--- Atualizar Dados Cadastrais ---")
    print("Deixe em branco para manter o valor atual")
    nome = input("Novo Nome: ")
    email = input("Novo E-mail: ")
    senha = input("Nova Senha: ")
    telefone = input("Novo Telefone: ")
    problema = input("Novo Problema/Sintoma: ")
    
    payload = {
        "id": id_paciente,
        "tipo": "paciente",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone,
        "info_extra": problema
    }
    
    try:
        resp = requests.put(f"{API_USUARIOS}/atualizar_usuario", json=payload)
        if resp.status_code == 200:
            dados = resp.json()
            if dados.get('sucesso'):
                print("Dados atualizados com sucesso!")
            else:
                print(f"Falha: {dados.get('mensagem')}")
        else:
            print(f"Erro: {resp.json()}")
    except Exception as e:
        print(f"Erro de conexão: {e}")


def pagar_consulta(id_paciente):
    print("\n--- Pagar Consulta Pendente ---")
    ver_minhas_consultas(id_paciente)
    
    id_consulta = input("\nID da consulta a pagar (0 para voltar): ")
    if id_consulta == '0':
        return
    
    print("\nFormas de pagamento:")
    print("1. Dinheiro")
    print("2. Cartão de Crédito")
    print("3. Cartão de Débito")
    print("4. PIX")
    
    opcao_pagamento = input("Escolha: ")
    formas = {'1': 'Dinheiro', '2': 'Cartão de Crédito', '3': 'Cartão de Débito', '4': 'PIX'}
    forma = formas.get(opcao_pagamento, 'Particular')
    
    valor = input("Valor da consulta (ex: 150.00): ")
    if not valor:
        valor = "150.00"
    
    payload = {
        "id_consulta": int(id_consulta),
        "valor": float(valor),
        "forma_pagamento": forma
    }
    
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/pagar_consulta", json=payload)
        if resp.status_code == 200:
            dados = resp.json()
            if dados.get('sucesso'):
                print("Pagamento realizado com sucesso! Consulta confirmada.")
            else:
                print(f"Falha: {dados.get('mensagem')}")
        else:
            print(f"Erro: {resp.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")


def excluir_conta(id_paciente):
    print("\n--- Excluir Conta ---")
    confirmacao = input("Tem certeza que deseja excluir sua conta? (s/n): ")
    
    if confirmacao.lower() != 's':
        print("Operação cancelada.")
        return False
    
    payload = {
        "id": id_paciente,
        "tipo": "paciente"
    }
    
    try:
        resp = requests.delete(f"{API_USUARIOS}/deletar_usuario", json=payload)
        if resp.status_code == 200:
            dados = resp.json()
            if dados.get('sucesso'):
                print("Conta excluída com sucesso!")
                return True
            else:
                print(f"Falha: {dados.get('mensagem')}")
        else:
            print(f"Erro: {resp.json()}")
    except Exception as e:
        print(f"Erro de conexão: {e}")
    return False

def agendar(id_paciente):
    print("\n--- Agendar Consulta ---")
    id_medico = input("ID do Médico (ex: 1): ")
    data = input("Data (AAAA-MM-DD): ")
    horario = input("Horário (HH:MM:SS): ")
    
    payload = {
        "id_paciente": id_paciente,
        "id_medico": id_medico,
        "data": data,
        "horario": horario
    }
    
    try:
        # Chama a interface de agendamento (Porta 8081)
        resp = requests.post(f"{API_AGENDAMENTO}/agendar", json=payload)
        print("Resposta do Servidor:", resp.json())
    except Exception as e:
        print(f"Erro de conexão com Agendamento: {e}")

def ver_minhas_consultas(id_paciente):
    print("\n--- Minhas Consultas ---")
    
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/listar_meus_agendamentos", json={"id_paciente": id_paciente})
        if resp.status_code == 200:
            consultas = resp.json()
            if not consultas:
                print("Nenhuma consulta encontrada.")
            else:
                for c in consultas:
                    print(f"[ID: {c['id_consulta']}] {c['data_consulta']} às {c['horario_consulta']} - Dr(a). {c['nome_medico']} ({c['status']})")
        else:
            print(f"Erro: {resp.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

def cancelar_consulta(id_paciente):
    print("\n--- Cancelar Consulta ---")
    ver_minhas_consultas(id_paciente)  # Mostra as consultas primeiro
    
    id_consulta = input("\nID da consulta a cancelar (0 para voltar): ")
    if id_consulta == '0':
        return
    
    confirmacao = input("Confirma cancelamento? (s/n): ")
    if confirmacao.lower() != 's':
        print("Operação cancelada.")
        return
    
    payload = {
        "id_consulta": int(id_consulta),
        "id_paciente": id_paciente
    }
    
    try:
        resp = requests.delete(f"{API_AGENDAMENTO}/cancelar_agendamento", json=payload)
        if resp.status_code == 200:
            dados = resp.json()
            if dados.get('sucesso'):
                print("Consulta cancelada com sucesso!")
            else:
                print(f"Falha: {dados.get('mensagem')}")
        else:
            print(f"Erro: {resp.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

if __name__ == "__main__":
    menu_principal()
