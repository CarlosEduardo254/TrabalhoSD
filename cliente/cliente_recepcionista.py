import requests
import sys

# Configurações de conexão
API_USUARIOS = "http://localhost:8083"
API_AGENDAMENTO = "http://localhost:8081"

def menu_principal():
    while True:
        print("\n=== SYSTEM HOSPITALAR: RECEPCIONISTA ===")
        print("1. Cadastrar")
        print("2. Login")
        print("0. Sair")
        opcao = input("Opção: ")

        if opcao == '1':
            cadastrar_recepcionista()
        elif opcao == '2':
            fazer_login()
        elif opcao == '0':
            sys.exit()
        else:
            print("Opção inválida.")

def cadastrar_recepcionista():
    print("\n--- Cadastro de Recepcionista ---")
    nome = input("Nome Completo: ")
    email = input("E-mail: ")
    senha = input("Senha: ")
    telefone = input("Telefone: ")
    
    payload = {
        "tipo": "recepcionista",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone
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
    print("\n--- Login Recepcionista ---")
    email = input("E-mail: ")
    senha = input("Senha: ")
    
    payload = {"email": email, "senha": senha}
    
    try:
        resp = requests.post(f"{API_USUARIOS}/login", json=payload)
        if resp.status_code == 200:
            dados = resp.json()
            if dados.get("perfil") == "recepcionista":
                menu_area_logada(dados)
            else:
                print("Login Negado: Este painel é apenas para RECEPCIONISTAS.")
        else:
            print(f"Login falhou: {resp.json()}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

def menu_area_logada(dados_usuario):
    print(f"\nBem-vindo(a), {dados_usuario['nome']}!")
    id_recep = dados_usuario['id']
    
    while True:
        print("\n--- Painel Recepcionista ---")
        print("1. Ver Agendamentos do Médico")
        print("2. Agendar Consulta para Paciente")
        print("3. Registrar Pagamento")
        print("4. Cancelar Consulta")
        print("5. Atualizar Dados Cadastrais")
        print("6. Excluir Conta")
        print("0. Logout")
        
        opcao = input("Opção: ")
        
        if opcao == '1':
            ver_agendamentos()
        elif opcao == '2':
            agendar_para_paciente()
        elif opcao == '3':
            registrar_pagamento_recep()
        elif opcao == '4':
            cancelar_consulta_recep()
        elif opcao == '5':
            atualizar_dados(id_recep)
        elif opcao == '6':
            if excluir_conta(id_recep):
                return
        elif opcao == '0':
            return
        else:
            print("Opção inválida.")

def ver_agendamentos():
    print("\n--- Agendamentos ---")
    id_medico = input("ID do Médico: ")

    if not id_medico:
        print("ID do médico é obrigatório.")
        return
    
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/listar_agenda", json={"id_medico": int(id_medico)})
        
        if resp.status_code == 200:
            agendamentos = resp.json()
            if not agendamentos:
                print("Nenhum agendamento encontrado.")
            else:
                for ag in agendamentos:
                    print(f"- [{ag.get('data_consulta')} às {ag.get('horario_consulta')}] Paciente: {ag.get('nome_paciente', 'N/A')} - Status: {ag.get('status')}")
        else:
            print(f"Erro: {resp.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

def agendar_para_paciente():
    print("\n--- Agendar Consulta ---")
    id_paciente = input("ID do Paciente: ")
    id_medico = input("ID do Médico: ")
    data = input("Data (AAAA-MM-DD): ")
    horario = input("Horário (HH:MM:SS): ")
    
    payload = {
        "id_paciente": id_paciente,
        "id_medico": id_medico,
        "data": data,
        "horario": horario
    }
    
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/agendar", json=payload)
        print("Resposta:", resp.json())
    except Exception as e:
        print(f"Erro de conexão: {e}")

def atualizar_dados(id_recep):
    print("\n--- Atualizar Dados Cadastrais ---")
    print("Deixe em branco para manter o valor atual")
    nome = input("Novo Nome: ")
    email = input("Novo E-mail: ")
    senha = input("Nova Senha: ")
    telefone = input("Novo Telefone: ")
    
    payload = {
        "id": id_recep,
        "tipo": "recepcionista",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone
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

def registrar_pagamento_recep():
    print("\n--- Registrar Pagamento ---")
    
    # Primeiro mostra as consultas de um médico
    id_medico = input("ID do Médico para ver consultas pendentes: ")
    if not id_medico:
        print("ID do médico é obrigatório.")
        return
    
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/listar_agenda", json={"id_medico": int(id_medico)})
        if resp.status_code == 200:
            consultas = resp.json()
            pendentes = [c for c in consultas if c.get('status') == 'PENDENTE']
            if not pendentes:
                print("Nenhuma consulta pendente encontrada.")
                return
            print("\n--- Consultas Pendentes ---")
            for c in pendentes:
                print(f"[ID: {c.get('id_consulta')}] {c['data_consulta']} às {c['horario_consulta']} - Paciente: {c['nome_paciente']}")
        else:
            print(f"Erro: {resp.text}")
            return
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return
    
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
    forma = formas.get(opcao_pagamento, 'Dinheiro')
    
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
                print("Pagamento registrado com sucesso! Consulta confirmada.")
            else:
                print(f"Falha: {dados.get('mensagem')}")
        else:
            print(f"Erro: {resp.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

def excluir_conta(id_recep):
    print("\n--- Excluir Conta ---")
    confirmacao = input("Tem certeza que deseja excluir sua conta? (s/n): ")
    
    if confirmacao.lower() != 's':
        print("Operação cancelada.")
        return False
    
    payload = {
        "id": id_recep,
        "tipo": "recepcionista"
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

def cancelar_consulta_recep():
    print("\n--- Cancelar Consulta ---")
    
    # Recepcionista pode ver a agenda de qualquer médico primeiro
    id_medico = input("ID do Médico para ver consultas: ")
    
    if not id_medico:
        print("ID do médico é obrigatório.")
        return
    
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/listar_agenda", json={"id_medico": int(id_medico)})
        if resp.status_code == 200:
            consultas = resp.json()
            if not consultas:
                print("Nenhuma consulta encontrada para este médico.")
                return
            else:
                print("\n--- Consultas do Médico ---")
                for c in consultas:
                    print(f"[ID: {c.get('id_consulta', 'N/A')}] {c['data_consulta']} às {c['horario_consulta']} - Paciente: {c['nome_paciente']} ({c['status']})")
        else:
            print(f"Erro: {resp.text}")
            return
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return
    
    id_consulta = input("\nID da consulta a cancelar (0 para voltar): ")
    if id_consulta == '0':
        return
    
    confirmacao = input("Confirma cancelamento? (s/n): ")
    if confirmacao.lower() != 's':
        print("Operação cancelada.")
        return
    
    # Recepcionista não passa id_paciente - pode cancelar qualquer uma
    payload = {"id_consulta": int(id_consulta)}
    
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