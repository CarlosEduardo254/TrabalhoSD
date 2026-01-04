import mysql.connector
import socket
import json
import time

def setup_db():
    print("--- 1. PREPARANDO BANCO DE DADOS ---")
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3307,
            user='root',
            password='123',
            database='hospital_db'
        )
        cursor = conn.cursor()
        
        # Inserir Medico
        cursor.execute("SELECT * FROM medico WHERE id_med = 1")
        if not cursor.fetchone():
            print("Inserindo Medico ID 1...")
            cursor.execute("""
                INSERT INTO medico (id_med, nome_med, especialidade, telefone, email, senha)
                VALUES (1, 'Dr. House', 'Diagnostico', '99999999', 'house@hospital.com', '1234')
            """)
        else:
            print("Medico ID 1 ja existe.")
            
        # Inserir Paciente
        cursor.execute("SELECT * FROM paciente WHERE id_usuario = 1")
        if not cursor.fetchone():
            print("Inserindo Paciente ID 1...")
            cursor.execute("""
                INSERT INTO paciente (id_usuario, nome, problema, telefone, email, senha)
                VALUES (1, 'Fulano de Tal', 'Checkup', '88888888', 'fulano@teste.com', '1234')
            """)
        else:
            print("Paciente ID 1 ja existe.")
            
        conn.commit()
        cursor.close()
        conn.close()
        print("Banco de dados pronto!")
        return True
    except Exception as e:
        print(f"ERRO DE BANCO: {e}")
        print("Certifique-se que instalou: pip install mysql-connector-python")
        return False

def test_agendamento():
    print("\n--- 2. TESTANDO AGENDAMENTO (Via Socket) ---")
    host = 'localhost'
    port = 5000
    
    dados = {
        "id_medico": 1,
        "id_paciente": 1,
        "data": "2024-12-25",
        "horario": "15:30"
    }

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5) # Timeout de 5s para não travar
        client.connect((host, port))
        
        print(f"Enviando JSON para {host}:{port} -> {json.dumps(dados)}")
        client.send(json.dumps(dados).encode('utf-8'))
        
        print("Aguardando resposta...")
        response = client.recv(4096)
        print(f"RESPOSTA DO SERVIDOR: {response.decode('utf-8')}")
        
        client.close()
    except Exception as e:
        print(f"ERRO DE CONEXAO: {e}")

if __name__ == "__main__":
    if setup_db():
        test_agendamento()
