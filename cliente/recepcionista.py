"""
Script CLI para operações de RECEPCIONISTA no sistema hospitalar.
Uso: python recepcionista.py <acao> [argumentos...]

Exemplos:
  python recepcionista.py criar "Fernanda Lima" "fernanda@hospital.com" "recep123" "88999993331"
  python recepcionista.py login "fernanda@hospital.com" "recep123"
  python recepcionista.py agenda <id_medico>
  python recepcionista.py agendar <id_paciente> <id_medico> <data> <horario> [particular]
  python recepcionista.py particular <id_paciente> <id_medico> <data> <horario>
  python recepcionista.py cancelar <id_consulta>
  python recepcionista.py pagar <id_consulta> <valor> <forma_pagamento>
  python recepcionista.py atualizar <id_recep> <nome> <email> <senha> <telefone>
  python recepcionista.py deletar <id_recep>

Notas:
  - Usar 'particular' como 5º argumento do agendar OU usar o comando 'particular' para consulta sem convênio
  - Consultas particulares ficam PENDENTE até o pagamento ser registrado
"""
import requests
import sys

# Configurações de conexão
API_USUARIOS = "http://localhost:8083"
API_AGENDAMENTO = "http://localhost:8081"

def criar(nome, email, senha, telefone):
    """Cria um novo recepcionista"""
    payload = {
        "tipo": "recepcionista",
        "nome": nome,
        "email": email,
        "senha": senha,
        "telefone": telefone
    }
    try:
        resp = requests.post(f"{API_USUARIOS}/criar_usuario", json=payload, timeout=10)
        dados = resp.json()
        if resp.status_code == 200 and dados.get('id') != 0:
            print(f"SUCESSO: Recepcionista criado com ID {dados.get('id')}")
        else:
            print(f"ERRO: {dados.get('mensagem', resp.text)}")
    except Exception as e:
        print(f"ERRO: {e}")

def login(email, senha):
    """Realiza login do recepcionista"""
    payload = {"email": email, "senha": senha}
    try:
        resp = requests.post(f"{API_USUARIOS}/login", json=payload, timeout=10)
        dados = resp.json()
        if resp.status_code == 200 and dados.get("status") == "sucesso":
            if dados.get("perfil") == "recepcionista":
                print(f"SUCESSO: Login realizado!")
                print(f"  ID: {dados.get('id')}")
                print(f"  Nome: {dados.get('nome')}")
                print(f"  Perfil: {dados.get('perfil')}")
            else:
                print(f"ERRO: Este usuário não é um recepcionista (perfil: {dados.get('perfil')})")
        else:
            print(f"ERRO: {dados.get('mensagem', 'Login falhou')}")
    except Exception as e:
        print(f"ERRO: {e}")

def agenda(id_medico):
    """Lista agenda de um médico"""
    payload = {"id_medico": int(id_medico)}
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/listar_agenda", json=payload, timeout=10)
        consultas = resp.json()
        if isinstance(consultas, list):
            if not consultas:
                print("INFO: Nenhuma consulta agendada.")
            else:
                print("AGENDA DO MÉDICO:")
                for c in consultas:
                    print(f"  ID: {c['id_consulta']} | Data: {c['data_consulta']} | Hora: {c['horario_consulta']} | Paciente: {c.get('nome_paciente', 'N/A')} | Status: {c['status']}")
        else:
            print(f"ERRO: {consultas}")
    except Exception as e:
        print(f"ERRO: {e}")

def agendar(id_paciente, id_medico, data, horario, particular=False):
    """Agenda uma consulta para um paciente (convênio ou particular)"""
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

def cancelar(id_consulta):
    """Cancela uma consulta (sem verificar paciente)"""
    payload = {"id_consulta": int(id_consulta)}
    try:
        resp = requests.delete(f"{API_AGENDAMENTO}/cancelar_agendamento", json=payload, timeout=10)
        dados = resp.json()
        if dados.get('sucesso'):
            print(f"SUCESSO: {dados.get('mensagem')}")
        else:
            print(f"ERRO: {dados.get('mensagem', resp.text)}")
    except Exception as e:
        print(f"ERRO: {e}")

def pagar(id_consulta, valor, forma_pagamento):
    """Registra pagamento de uma consulta"""
    payload = {
        "id_consulta": int(id_consulta),
        "valor": float(valor),
        "forma_pagamento": forma_pagamento
    }
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/pagar_consulta", json=payload, timeout=10)
        dados = resp.json()
        if dados.get('sucesso'):
            print(f"SUCESSO: {dados.get('mensagem')}")
        else:
            print(f"ERRO: {dados.get('mensagem', resp.text)}")
    except Exception as e:
        print(f"ERRO: {e}")

def atualizar(id_recep, nome, email, senha, telefone):
    """Atualiza dados do recepcionista"""
    payload = {
        "id": int(id_recep),
        "tipo": "recepcionista",
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

def deletar(id_recep):
    """Deleta conta do recepcionista"""
    payload = {"id": int(id_recep), "tipo": "recepcionista"}
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
    elif acao == "agenda" and len(args) == 1:
        agenda(args[0])
    elif acao == "agendar" and len(args) >= 4:
        particular = len(args) >= 5 and args[4].lower() == "particular"
        agendar(args[0], args[1], args[2], args[3], particular)
    elif acao == "particular" and len(args) == 4:
        agendar(args[0], args[1], args[2], args[3], particular=True)
    elif acao == "cancelar" and len(args) == 1:
        cancelar(args[0])
    elif acao == "pagar" and len(args) == 3:
        pagar(args[0], args[1], args[2])
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
