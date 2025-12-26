import socket
import threading
import mysql.connector
import json
import sys
import traceback

# Configuração do Banco
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': '123',
    'database': 'hospital_db'
}

def conectar_banco():
    return mysql.connector.connect(**DB_CONFIG)

def agendar_consulta(id_medico, id_paciente, data, horario):
    conn = None
    try:
        conn = conectar_banco()
        cursor = conn.cursor()

        # Verifica disponibilidade
        query_check = """
            SELECT count(*) FROM consulta 
            WHERE id_medico = %s AND data_consulta = %s AND horario_consulta = %s
        """
        cursor.execute(query_check, (id_medico, data, horario))
        (ocupado,) = cursor.fetchone()

        if ocupado > 0:
            return "ERRO: Médico indisponível."

        # Insere
        query_insert = """
            INSERT INTO consulta (id_medico, id_paciente, data_consulta, horario_consulta, status)
            VALUES (%s, %s, %s, %s, 'Agendada')
        """
        cursor.execute(query_insert, (id_medico, id_paciente, data, horario))
        conn.commit()
        return f"SUCESSO: Agendado para {data} as {horario}."

    except mysql.connector.Error as err:
        return f"ERRO DE BANCO: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def processar_cliente(con, endereco):
    print(f"[Socket] Cliente conectado: {endereco}", flush=True)
    try:
        while True:
            mensagem = con.recv(4096)
            if not mensagem: break
            
            dados_str = mensagem.decode('utf-8')
            print(f"[Socket] Recebido: {dados_str}", flush=True)
            
            try:
                dados = json.loads(dados_str)
                resposta = agendar_consulta(
                    dados['id_medico'], 
                    dados['id_paciente'], 
                    dados['data'], 
                    dados['horario']
                )
            except Exception as e:
                resposta = f"ERRO JSON/LOGICA: {str(e)}"
            
            con.send(resposta.encode('utf-8'))
    except Exception as e:
        print(f"Erro na conexão: {e}", flush=True)
    finally:
        con.close()

# --- BLOCO PRINCIPAL BLINDADO ---
if __name__ == "__main__":
    try:
        print(">>> INICIANDO SERVIÇO DE AGENDAMENTO...", flush=True)
        
        # Cria o Socket
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Tenta alocar a porta (Bind)
        try:
            tcp.bind(('0.0.0.0', 5000))
        except OSError as e:
            print(f"ERRO FATAL: A porta 5000 já está em uso! Feche outros terminais python.\nErro: {e}")
            sys.exit(1)
            
        tcp.listen(5)
        print(">>> SERVIÇO RODANDO NA PORTA 5000! (Não feche essa janela)", flush=True)

        while True:
            con, endereco = tcp.accept()
            threading.Thread(target=processar_cliente, args=(con, endereco)).start()

    except Exception:
        print("ERRO DESCONHECIDO:", flush=True)
        traceback.print_exc()