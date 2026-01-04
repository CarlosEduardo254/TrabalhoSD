import requests
import sys

# Configurações de conexão
API_USUARIOS = "http://localhost:8083"
API_AGENDAMENTO = "http://localhost:8081"

def menu_principal():
    while True:
        print("\n=== SYSTEM HOSPITALAR: MÉDICO ===")
        print("1. Cadastrar")
        print("2. Login")
        print("0. Sair")
        opcao = input("Opção: ")

        if opcao == '1':
            cadastrar_medico()
        elif opcao == '2':
            fazer_login()
        elif opcao == '0':
            sys.exit()
        else:
            print("Opção inválida.")

def cadastrar_medico():
    print("\n--- Cadastro de Médico ---")
    nome = input("Nome Completo: ")
    email = input("E-mail: ")
    senha = input("Senha: ")
    telefone = input("Telefone: ")
    crm = input("CRM: ")
    
    payload = {
        "tipo": "medico",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone,
        "info_extra": crm # No backend, info_extra é usado como CRM para médicos
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
    print("\n--- Login Médico ---")
    email = input("E-mail: ")
    senha = input("Senha: ")
    
    payload = {"email": email, "senha": senha}
    
    try:
        resp = requests.post(f"{API_USUARIOS}/login", json=payload)
        if resp.status_code == 200:
            dados = resp.json()
            if dados.get("perfil") == "medico":
                menu_area_logada(dados)
            else:
                print("Login Negado: Este painel é apenas para MÉDICOS.")
        else:
            print(f"Login falhou: {resp.json()}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

def menu_area_logada(dados_usuario):
    print(f"\nBem-vindo, Dr(a). {dados_usuario['nome']}!")
    
    while True:
        print("\n--- Painel Médico ---")
        print("1. Ver Minha Agenda")
        print("0. Logout")
        
        opcao = input("Opção: ")
        
        if opcao == '1':
            try:
                # Chama a rota da Interface (8081)
                resp = requests.post(f"{API_AGENDAMENTO}/listar_agenda", json={"id_medico": dados_usuario['id']})

                if resp.status_code == 200:
                    agendamentos = resp.json()
                    # Se vinher uma lista
                    print("\n--- Agenda do Médico ---")
                    if not agendamentos:
                        print("Nenhum agendamento encontrado.")
                    else:
                        for agendamento in agendamentos:
                            print(f"- [{agendamento['data_consulta']} as {agendamento['horario_consulta']}] {agendamento['nome_paciente']} ({agendamento['status']})")
                else:
                    print(f"Erro ao buscar agenda: {resp.text}")
            except Exception as e:
                print(f"Erro de conexão: {e}")
        elif opcao == '0':
            return
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu_principal()
