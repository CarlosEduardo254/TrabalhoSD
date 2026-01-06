"""
Script CLI para operações de ADMINISTRADOR no sistema hospitalar.
Uso: python admin.py <acao> [argumentos...]

Exemplos:
  python admin.py criar "Admin Sistema" "admin@hospital.com" "admin123" "88999990000"
  python admin.py login "admin@hospital.com" "admin123"
  python admin.py listar_pacientes
  python admin.py listar_medicos
  python admin.py listar_recepcionistas
  python admin.py listar_admins
  python admin.py listar_todos
  python admin.py atualizar <id_admin> <nome> <email> <senha> <telefone>
  python admin.py deletar <id_admin>
"""
import requests
import sys

# Configurações de conexão
API_USUARIOS = "http://localhost:8083"
API_AGENDAMENTO = "http://localhost:8081"

def criar(nome, email, senha, telefone):
    """Cria um novo administrador"""
    payload = {
        "tipo": "admin",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone
    }
    try:
        resp = requests.post(f"{API_USUARIOS}/criar_usuario", json=payload, timeout=10)
        dados = resp.json()
        if resp.status_code == 200 and dados.get('id') != 0:
            print(f"SUCESSO: Administrador criado com ID {dados.get('id')}")
        else:
            print(f"ERRO: {dados.get('mensagem', resp.text)}")
    except Exception as e:
        print(f"ERRO: {e}")

def login(email, senha):
    """Realiza login do administrador"""
    payload = {"email": email, "senha": senha}
    try:
        resp = requests.post(f"{API_USUARIOS}/login", json=payload, timeout=10)
        dados = resp.json()
        if resp.status_code == 200 and dados.get("status") == "sucesso":
            if dados.get("perfil") == "administradores":
                print(f"SUCESSO: Login realizado!")
                print(f"  ID: {dados.get('id')}")
                print(f"  Nome: {dados.get('nome')}")
                print(f"  Perfil: {dados.get('perfil')}")
            else:
                print(f"ERRO: Este usuário não é um administrador (perfil: {dados.get('perfil')})")
        else:
            print(f"ERRO: {dados.get('mensagem', 'Login falhou')}")
    except Exception as e:
        print(f"ERRO: {e}")

def listar_usuarios(tipo):
    """Lista usuários por tipo"""
    payload = {"tipo": tipo}
    try:
        resp = requests.post(f"{API_USUARIOS}/listar_usuarios", json=payload, timeout=10)
        usuarios = resp.json()
        if isinstance(usuarios, list):
            if not usuarios:
                print(f"INFO: Nenhum usuário do tipo '{tipo}' encontrado.")
            else:
                print(f"USUÁRIOS ({tipo.upper()}):")
                for u in usuarios:
                    info = u.get('info_extra', '')
                    extra = ""
                    if u['tipo'] == 'medico':
                        extra = f" | CRM: {info}"
                    elif u['tipo'] == 'paciente':
                        extra = f" | Problema: {info}"
                    print(f"  ID: {u['id']} | Nome: {u['nome']} | Email: {u['email']} | Tel: {u['telefone']}{extra}")
        else:
            print(f"ERRO: {usuarios}")
    except Exception as e:
        print(f"ERRO: {e}")

def atualizar(id_admin, nome, email, senha, telefone):
    """Atualiza dados do administrador"""
    payload = {
        "id": int(id_admin),
        "tipo": "admin",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone
    }
    try:
        resp = requests.put(f"{API_USUARIOS}/atualizar_usuario", json=payload, timeout=10)
        dados = resp.json()
        if dados.get('sucesso'):
            print(f"SUCESSO: {dados.get('mensagem')}")
        else:
            print(f"ERRO: {dados.get('mensagem', resp.text)}")
    except Exception as e:
        print(f"ERRO: {e}")

def deletar(id_admin):
    """Deleta conta do administrador"""
    payload = {"id": int(id_admin), "tipo": "admin"}
    try:
        resp = requests.delete(f"{API_USUARIOS}/deletar_usuario", json=payload, timeout=10)
        dados = resp.json()
        if dados.get('sucesso'):
            print(f"SUCESSO: {dados.get('mensagem')}")
        else:
            print(f"ERRO: {dados.get('mensagem', resp.text)}")
    except Exception as e:
        print(f"ERRO: {e}")

def mostrar_ajuda():
    print(__doc__)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        mostrar_ajuda()
        sys.exit(1)
    
    acao = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if acao == "criar" and len(args) == 4:
        criar(args[0], args[1], args[2], args[3])
    elif acao == "login" and len(args) == 2:
        login(args[0], args[1])
    elif acao == "listar_pacientes":
        listar_usuarios("paciente")
    elif acao == "listar_medicos":
        listar_usuarios("medico")
    elif acao == "listar_recepcionistas":
        listar_usuarios("recepcionista")
    elif acao == "listar_admins":
        listar_usuarios("admin")
    elif acao == "listar_todos":
        listar_usuarios("todos")
    elif acao == "atualizar" and len(args) == 5:
        atualizar(args[0], args[1], args[2], args[3], args[4])
    elif acao == "deletar" and len(args) == 1:
        deletar(args[0])
    elif acao == "ajuda" or acao == "help":
        mostrar_ajuda()
    else:
        print(f"ERRO: Ação '{acao}' inválida ou argumentos incorretos.")
        mostrar_ajuda()
        sys.exit(1)
