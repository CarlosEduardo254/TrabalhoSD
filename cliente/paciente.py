"""
Script CLI para operações de PACIENTE no sistema hospitalar.
Uso: python paciente.py <acao> [argumentos...]

Exemplos:
  python paciente.py criar "José Silva" "jose@email.com" "senha123" "88999991111" "Dor de cabeça"
  python paciente.py login "jose@email.com" "senha123"
  python paciente.py agendar <id_paciente> <id_medico> <data> <horario> [particular]
  python paciente.py particular <id_paciente> <id_medico> <data> <horario>
  python paciente.py listar <id_paciente>
  python paciente.py cancelar <id_paciente> <id_consulta>
  python paciente.py atualizar <id_paciente> <nome> <email> <senha> <telefone> <problema>
  python paciente.py deletar <id_paciente>

Notas:
  - Usar 'particular' como 5º argumento do agendar OU usar o comando 'particular' para consulta sem convênio
  - Consultas com convênio: ID paciente PAR = aprovado, ÍMPAR = pendente (precisa pagar)
  - Consultas particulares: sempre ficam PENDENTE até o pagamento
  - Pagamentos são realizados apenas pela RECEPÇÃO (recepcionista.py)
"""
import requests
import sys

# Configurações de conexão
API_USUARIOS = "http://localhost:8083"
API_AGENDAMENTO = "http://localhost:8081"

def criar(nome, email, senha, telefone, problema):
    """Cria um novo paciente"""
    payload = {
        "tipo": "paciente",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone,
        "info_extra": problema
    }
    try:
        resp = requests.post(f"{API_USUARIOS}/criar_usuario", json=payload, timeout=10)
        dados = resp.json()
        if resp.status_code == 200 and dados.get('id') != 0:
            print(f"SUCESSO: Paciente criado com ID {dados.get('id')}")
        else:
            print(f"ERRO: {dados.get('mensagem', resp.text)}")
    except Exception as e:
        print(f"ERRO: {e}")

def login(email, senha):
    """Realiza login do paciente"""
    payload = {"email": email, "senha": senha}
    try:
        resp = requests.post(f"{API_USUARIOS}/login", json=payload, timeout=10)
        dados = resp.json()
        if resp.status_code == 200 and dados.get("status") == "sucesso":
            if dados.get("perfil") == "paciente":
                print(f"SUCESSO: Login realizado!")
                print(f"  ID: {dados.get('id')}")
                print(f"  Nome: {dados.get('nome')}")
                print(f"  Perfil: {dados.get('perfil')}")
            else:
                print(f"ERRO: Este usuário não é um paciente (perfil: {dados.get('perfil')})")
        else:
            print(f"ERRO: {dados.get('mensagem', 'Login falhou')}")
    except Exception as e:
        print(f"ERRO: {e}")

def agendar(id_paciente, id_medico, data, horario, particular=False):
    """Agenda uma consulta (convênio ou particular)"""
    payload = {
        "id_paciente": int(id_paciente),
        "id_medico": int(id_medico),
        "data": data,
        "horario": horario,
        "particular": particular
    }
    
    tipo_consulta = "PARTICULAR" if particular else "CONVÊNIO"
    print(f"INFO: Agendando consulta {tipo_consulta}...")
    
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/agendar", json=payload, timeout=10)
        dados = resp.json()
        resposta = dados.get('resposta_do_servico', '')
        
        if "SUCESSO" in resposta:
            print(f"SUCESSO: {resposta}")
            if particular:
                print("      Consulta particular - aguardando pagamento para confirmação.")
        elif "Paciente não encontrado" in resposta:
            print(f"ERRO: Paciente ID {id_paciente} não está cadastrado no sistema!")
            print("      Use: python paciente.py criar <nome> <email> <senha> <telefone> <problema>")
        elif "indisponível" in resposta.lower() or "horário" in resposta.lower():
            print(f"ERRO: Médico indisponível neste horário!")
            print(f"      Data: {data} | Horário: {horario}")
            print("      Tente outro horário ou data.")
        else:
            # Mostra a mensagem bruta do servidor para não interpretar errado
            print(f"ERRO: {resposta}")
    except Exception as e:
        print(f"ERRO: {e}")

def listar(id_paciente):
    """Lista consultas do paciente"""
    payload = {"id_paciente": int(id_paciente)}
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/listar_meus_agendamentos", json=payload, timeout=10)
        consultas = resp.json()
        if isinstance(consultas, list):
            if not consultas:
                print("INFO: Nenhuma consulta encontrada.")
            else:
                print("CONSULTAS:")
                for c in consultas:
                    print(f"  ID: {c['id_consulta']} | Data: {c['data_consulta']} | Hora: {c['horario_consulta']} | Médico: {c.get('nome_medico', 'N/A')} | Status: {c['status']}")
        else:
            print(f"ERRO: {consultas}")
    except Exception as e:
        print(f"ERRO: {e}")

def cancelar(id_paciente, id_consulta):
    """Cancela uma consulta"""
    payload = {"id_paciente": int(id_paciente), "id_consulta": int(id_consulta)}
    try:
        resp = requests.delete(f"{API_AGENDAMENTO}/cancelar_agendamento", json=payload, timeout=10)
        dados = resp.json()
        if dados.get('sucesso'):
            print(f"SUCESSO: {dados.get('mensagem')}")
        else:
            print(f"ERRO: {dados.get('mensagem', resp.text)}")
    except Exception as e:
        print(f"ERRO: {e}")


def atualizar(id_paciente, nome, email, senha, telefone, problema):
    """Atualiza dados do paciente"""
    payload = {
        "id": int(id_paciente),
        "tipo": "paciente",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone,
        "info_extra": problema
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

def deletar(id_paciente):
    """Deleta conta do paciente"""
    payload = {"id": int(id_paciente), "tipo": "paciente"}
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
    elif acao == "agendar" and len(args) >= 4:
        particular = len(args) >= 5 and args[4].lower() == "particular"
        agendar(args[0], args[1], args[2], args[3], particular)
    elif acao == "particular" and len(args) == 4:
        agendar(args[0], args[1], args[2], args[3], particular=True)
    elif acao == "listar" and len(args) == 1:
        listar(args[0])
    elif acao == "cancelar" and len(args) == 2:
        cancelar(args[0], args[1])
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
