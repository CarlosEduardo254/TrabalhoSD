"""
Script CLI para operações de MÉDICO no sistema hospitalar.
Uso: python medico.py <acao> [argumentos...]

Exemplos:
  python medico.py criar "Dr. João Silva" "joao@hospital.com" "senha123" "88999991111" "12345-CE"
  python medico.py login "joao@hospital.com" "senha123"
  python medico.py agenda <id_medico>
  python medico.py atualizar <id_medico> <nome> <email> <senha> <telefone> <crm>
  python medico.py deletar <id_medico>
"""
import requests
import sys

# Configurações de conexão
API_USUARIOS = "http://localhost:8083"
API_AGENDAMENTO = "http://localhost:8081"

def criar(nome, email, senha, telefone, crm):
    """Cria um novo médico"""
    payload = {
        "tipo": "medico",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone,
        "info_extra": crm
    }
    try:
        resp = requests.post(f"{API_USUARIOS}/criar_usuario", json=payload, timeout=10)
        dados = resp.json()
        if resp.status_code == 200 and dados.get('id') != 0:
            print(f"SUCESSO: Médico criado com ID {dados.get('id')}")
        else:
            print(f"ERRO: {dados.get('mensagem', resp.text)}")
    except Exception as e:
        print(f"ERRO: {e}")

def login(email, senha):
    """Realiza login do médico"""
    payload = {"email": email, "senha": senha}
    try:
        resp = requests.post(f"{API_USUARIOS}/login", json=payload, timeout=10)
        dados = resp.json()
        if resp.status_code == 200 and dados.get("status") == "sucesso":
            if dados.get("perfil") == "medico":
                print(f"SUCESSO: Login realizado!")
                print(f"  ID: {dados.get('id')}")
                print(f"  Nome: {dados.get('nome')}")
                print(f"  Perfil: {dados.get('perfil')}")
            else:
                print(f"ERRO: Este usuário não é um médico (perfil: {dados.get('perfil')})")
        else:
            print(f"ERRO: {dados.get('mensagem', 'Login falhou')}")
    except Exception as e:
        print(f"ERRO: {e}")

def agenda(id_medico):
    """Lista agenda do médico"""
    payload = {"id_medico": int(id_medico)}
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/listar_agenda", json=payload, timeout=10)
        consultas = resp.json()
        if isinstance(consultas, list):
            if not consultas:
                print("INFO: Nenhuma consulta agendada.")
            else:
                print("AGENDA:")
                for c in consultas:
                    print(f"  ID: {c['id_consulta']} | Data: {c['data_consulta']} | Hora: {c['horario_consulta']} | Paciente: {c.get('nome_paciente', 'N/A')} | Status: {c['status']}")
        else:
            print(f"ERRO: {consultas}")
    except Exception as e:
        print(f"ERRO: {e}")

def atualizar(id_medico, nome, email, senha, telefone, crm):
    """Atualiza dados do médico"""
    payload = {
        "id": int(id_medico),
        "tipo": "medico",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone,
        "info_extra": crm
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

def deletar(id_medico):
    """Deleta conta do médico"""
    payload = {"id": int(id_medico), "tipo": "medico"}
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
    
    if acao == "criar" and len(args) == 5:
        criar(args[0], args[1], args[2], args[3], args[4])
    elif acao == "login" and len(args) == 2:
        login(args[0], args[1])
    elif acao == "agenda" and len(args) == 1:
        agenda(args[0])
    elif acao == "atualizar" and len(args) == 6:
        atualizar(args[0], args[1], args[2], args[3], args[4], args[5])
    elif acao == "deletar" and len(args) == 1:
        deletar(args[0])
    elif acao == "ajuda" or acao == "help":
        mostrar_ajuda()
    else:
        print(f"ERRO: Ação '{acao}' inválida ou argumentos incorretos.")
        mostrar_ajuda()
        sys.exit(1)
