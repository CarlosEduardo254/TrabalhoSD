import requests
import sys

# Configurações de conexão
API_USUARIOS = "http://localhost:8083"
API_AGENDAMENTO = "http://localhost:8081"

def menu_principal():
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
        print("0. Logout")
        
        opcao = input("Opção: ")
        
        if opcao == '1':
            agendar(id_paciente)
        elif opcao == '0':
            return
        else:
            print("Opção inválida.")

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

if __name__ == "__main__":
    menu_principal()
