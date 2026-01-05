import requests
import sys

# Configurações de conexão
API_USUARIOS = "http://localhost:8083"
API_AGENDAMENTO = "http://localhost:8081"

def menu_principal():
    while True:
        print("\n=== SYSTEM HOSPITALAR: ADMINISTRADOR ===")
        print("1. Cadastrar")
        print("2. Login")
        print("0. Sair")
        opcao = input("Opção: ")

        if opcao == '1':
            cadastrar_admin()
        elif opcao == '2':
            fazer_login()
        elif opcao == '0':
            sys.exit()
        else:
            print("Opção inválida.")

def cadastrar_admin():
    print("\n--- Cadastro de Administrador ---")
    nome = input("Nome Completo: ")
    email = input("E-mail: ")
    senha = input("Senha: ")
    telefone = input("Telefone: ")
    
    payload = {
        "tipo": "admin",
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
    print("\n--- Login Administrador ---")
    email = input("E-mail: ")
    senha = input("Senha: ")
    
    payload = {"email": email, "senha": senha}
    
    try:
        resp = requests.post(f"{API_USUARIOS}/login", json=payload)
        if resp.status_code == 200:
            dados = resp.json()
            if dados.get("perfil") == "administradores":
                menu_area_logada(dados)
            else:
                print("Login Negado: Este painel é apenas para ADMINISTRADORES.")
        else:
            print(f"Login falhou: {resp.json()}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

def menu_area_logada(dados_usuario):
    print(f"\nBem-vindo(a), Admin {dados_usuario['nome']}!")
    id_admin = dados_usuario['id']
    
    while True:
        print("\n--- Painel Administrador ---")
        print("1. Listar Todos os Pacientes")
        print("2. Listar Todos os Médicos")
        print("3. Listar Todos os Usuários")
        print("4. Atualizar Dados Cadastrais")
        print("5. Excluir Conta")
        print("0. Logout")
        
        opcao = input("Opção: ")
        
        if opcao == '1':
            listar_usuarios("paciente")
        elif opcao == '2':
            listar_usuarios("medico")
        elif opcao == '3':
            listar_usuarios("todos")
        elif opcao == '4':
            atualizar_dados(id_admin)
        elif opcao == '5':
            if excluir_conta(id_admin):
                return
        elif opcao == '0':
            return
        else:
            print("Opção inválida.")

def listar_usuarios(tipo):
    print(f"\n--- Lista de Usuários ({tipo.upper()}) ---")
    
    try:
        resp = requests.post(f"{API_USUARIOS}/listar_usuarios", json={"tipo": tipo})
        if resp.status_code == 200:
            usuarios = resp.json()
            if not usuarios:
                print("Nenhum usuário encontrado.")
            else:
                print(f"{'ID':<5} {'TIPO':<12} {'NOME':<25} {'EMAIL':<25} {'TELEFONE':<15} {'INFO EXTRA'}")
                print("-" * 100)
                for u in usuarios:
                    info = u.get('info_extra', '')
                    if u['tipo'] == 'medico':
                        info = f"CRM: {info}"
                    elif u['tipo'] == 'paciente':
                        info = f"Problema: {info}"
                    print(f"{u['id']:<5} {u['tipo']:<12} {u['nome']:<25} {u['email']:<25} {u['telefone']:<15} {info}")
        else:
            print(f"Erro: {resp.text}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

def atualizar_dados(id_admin):
    print("\n--- Atualizar Dados Cadastrais ---")
    print("Deixe em branco para manter o valor atual")
    nome = input("Novo Nome: ")
    email = input("Novo E-mail: ")
    senha = input("Nova Senha: ")
    telefone = input("Novo Telefone: ")
    
    payload = {
        "id": id_admin,
        "tipo": "admin",
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

def excluir_conta(id_admin):
    print("\n--- Excluir Conta ---")
    confirmacao = input("Tem certeza que deseja excluir sua conta? (s/n): ")
    
    if confirmacao.lower() != 's':
        print("Operação cancelada.")
        return False
    
    payload = {
        "id": id_admin,
        "tipo": "admin"
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

if __name__ == "__main__":
    menu_principal()