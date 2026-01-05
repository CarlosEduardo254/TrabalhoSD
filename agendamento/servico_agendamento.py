import socket
import threading
import mysql.connector
import json
import sys
import traceback
import grpc
import usuario_pb2
import usuario_pb2_grpc
import socket
import json
import pika


# Configuração do Banco
DB_CONFIG = {
    'host': 'db',
    'port': 3306,
    'user': 'root',
    'password': '123',
    'database': 'hospital_db'
}

def conectar_banco():
    return mysql.connector.connect(**DB_CONFIG)

def notificar_consulta_confirmada(mensagem):
    """
    Envia notificação via RabbitMQ quando uma consulta é confirmada.
    """
    try:
        credentials = pika.PlainCredentials('user', 'password')
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue='email_queue')
        channel.basic_publish(exchange='', routing_key='email_queue', body=mensagem)
        print(f"[RabbitMQ] Notificação enviada: {mensagem}", flush=True)
        connection.close()
    except Exception as e:
        print(f"[RabbitMQ] Erro ao notificar: {e}", flush=True)

# Coordenação de fluxo do agendamento
def orquestrar_agendamento(dados):
    """
    Orquestra o fluxo completo de agendamento:
    - Verifica paciente
    - Cria consulta como PENDENTE
    - Valida convênio
    - Confirma consulta
    - Notifica via RabbitMQ

    dados: dict com informações da consulta
    """

    # 1. Verificar se paciente existe
    paciente_existe = verificar_paciente_grpc(int(dados["id_paciente"]))
    if not paciente_existe:
        return {
            "sucesso": False,
            "mensagem": "Paciente não encontrado"
        }

    # 2. Criar consulta como PENDENTE
    try:
        id_consulta = inserir_consulta(dados, status="PENDENTE")
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": "Erro ao criar consulta"
        }

    # 3. Chamar serviço de validação
    validado = validar_consulta_rmi(
        dados["id_paciente"],
        id_consulta
    )

    # 4. Atualizar status e notificar
    if validado:
        atualizar_status_consulta(id_consulta, "CONFIRMADA")

        notificar_consulta_confirmada(
            f"Consulta {id_consulta} confirmada para paciente {dados['id_paciente']}"
        )

        return {
            "sucesso": True,
            "status": "CONFIRMADA",
            "id_consulta": id_consulta
        }

    # 5. Caso não validado
    return {
        "sucesso": True,
        "status": "PENDENTE",
        "id_consulta": id_consulta
    }


def verificar_paciente_grpc(id_paciente) -> bool:
    """
    Verifica se o paciente existe no Serviço de Usuários via gRPC.
    Retorna True se existir, False caso contrário.
    """

    try:
        # Endereço do serviço de usuários (docker-compose)
        grpc_host = os.getenv('GRPC_SERVER_HOST', 'servico_usuarios')
        channel = grpc.insecure_channel(f'{grpc_host}:50051')
        stub = usuario_pb2_grpc.UsuarioServiceStub(channel)

        request = usuario_pb2.VerificarUsuarioRequest(
            id=id_paciente
        )

        response = stub.VerificarUsuario(request)

        return response.existe

    except Exception as e:
        print(f"[gRPC] Erro ao verificar paciente: {e}")
        return False
    

import os
import requests

def inserir_consulta(dados, status="PENDENTE"):
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        # Verificar disponibilidade
        query_check = """
            SELECT count(*) FROM consulta 
            WHERE id_medico = %s AND data_consulta = %s AND horario_consulta = %s
        """
        cursor.execute(query_check, (dados['id_medico'], dados['data'], dados['horario']))
        (ocupado,) = cursor.fetchone()

        if ocupado > 0:
            raise Exception("Médico indisponível neste horário")

        query_insert = """
            INSERT INTO consulta (id_medico, id_paciente, data_consulta, horario_consulta, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query_insert, (dados['id_medico'], dados['id_paciente'], dados['data'], dados['horario'], status))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def atualizar_status_consulta(id_consulta, novo_status):
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE consulta SET status = %s WHERE id_consulta = %s", (novo_status, id_consulta))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def cancelar_consulta(id_consulta, id_paciente=None):
    """
    Cancela uma consulta pelo ID.
    Se id_paciente for informado, verifica se a consulta pertence ao paciente.
    """
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verifica se a consulta existe
        if id_paciente:
            cursor.execute(
                "SELECT * FROM consulta WHERE id_consulta = %s AND id_paciente = %s",
                (id_consulta, id_paciente)
            )
        else:
            cursor.execute("SELECT * FROM consulta WHERE id_consulta = %s", (id_consulta,))
        
        consulta = cursor.fetchone()
        
        if not consulta:
            return {"sucesso": False, "mensagem": "Consulta não encontrada ou não pertence ao paciente"}
        
        # Deleta a consulta
        cursor.execute("DELETE FROM consulta WHERE id_consulta = %s", (id_consulta,))
        conn.commit()
        
        return {"sucesso": True, "mensagem": "Consulta cancelada com sucesso"}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao cancelar: {str(e)}"}
    finally:
        cursor.close()
        conn.close()

def listar_consultas_paciente(id_paciente):
    """
    Lista todas as consultas de um paciente
    """
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT c.id_consulta, c.data_consulta, c.horario_consulta, c.status, m.nome_med as nome_medico
            FROM consulta c
            JOIN medico m ON c.id_medico = m.id_med
            WHERE c.id_paciente = %s
            ORDER BY c.data_consulta, c.horario_consulta
        """
        cursor.execute(sql, (id_paciente,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar consultas do paciente: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def registrar_pagamento(id_consulta, valor, forma_pagamento):
    """
    Registra o pagamento de uma consulta e atualiza o status para CONFIRMADA.
    """
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        # Verifica se a consulta existe e está PENDENTE
        cursor.execute("SELECT status FROM consulta WHERE id_consulta = %s", (id_consulta,))
        resultado = cursor.fetchone()
        
        if not resultado:
            return {"sucesso": False, "mensagem": "Consulta não encontrada"}
        
        if resultado[0] == "CONFIRMADA":
            return {"sucesso": False, "mensagem": "Consulta já está confirmada"}
        
        # Registra o pagamento
        cursor.execute("""
            INSERT INTO pagamento (id_consulta, valor, forma_pagamento, status_validacao)
            VALUES (%s, %s, %s, 'PAGO')
        """, (id_consulta, valor, forma_pagamento))
        
        # Atualiza o status da consulta para CONFIRMADA
        cursor.execute("UPDATE consulta SET status = 'CONFIRMADA' WHERE id_consulta = %s", (id_consulta,))
        
        conn.commit()
        
        return {"sucesso": True, "mensagem": "Pagamento registrado e consulta confirmada"}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao processar pagamento: {str(e)}"}
    finally:
        cursor.close()
        conn.close()

def validar_consulta_rmi(id_paciente, id_consulta) -> bool:
    """
    Simula validação de convênio.
    Regra: ID do paciente par = convênio aprovado
           ID do paciente ímpar = convênio rejeitado (precisa pagar)
    
    Em produção, isso chamaria um serviço RMI externo.
    """
    print(f"[Validação] Verificando convênio para paciente {id_paciente}", flush=True)
    
    aprovado = int(id_paciente) % 2 == 0
    
    print(f"[Validação] Resultado: {'APROVADO' if aprovado else 'REJEITADO'}", flush=True)
    return aprovado

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
                # Valida se tem campo 'acao'
                acao = dados.get('acao', 'agendar') # Default para manter compatibilidade se necessário

                if acao == 'agendar':
                    # CHAMA ORQUESTRADOR AO INVES DE IR DIRETO NO BANCO
                    resultado = orquestrar_agendamento(dados)
                    
                    # Formata resposta p/ cliente
                    if resultado['sucesso']:
                         resposta = f"SUCESSO: Consulta {resultado['id_consulta']} agendada. Status: {resultado.get('status')}"
                    else:
                         resposta = f"ERRO: {resultado['mensagem']}"

                elif acao == 'listar_medico':
                    lista = listar_agendamentos_medico(dados.get('id_medico'))
                    resposta = json.dumps(lista, default=str) # Serializa lista para JSON string
                
                elif acao == 'listar_paciente':
                    lista = listar_consultas_paciente(int(dados.get('id_paciente')))
                    resposta = json.dumps(lista, default=str)

                elif acao == 'pagar':
                    resultado = registrar_pagamento(
                        int(dados.get('id_consulta')),
                        float(dados.get('valor', 150.00)),
                        dados.get('forma_pagamento', 'Particular')
                    )
                    resposta = json.dumps(resultado)
                    
                elif acao == 'cancelar':
                    id_paciente = dados.get('id_paciente')
                    resultado = cancelar_consulta(
                        int(dados.get('id_consulta')),
                        int(id_paciente) if id_paciente else None
                    )
                    resposta = json.dumps(resultado)

                else:
                     resposta = "ERRO: Ação desconhecida"
                     
            except Exception as e:
                resposta = f"ERRO CRITICO: {str(e)}"
                traceback.print_exc()
            
            con.send(resposta.encode('utf-8'))
    except Exception as e:
        print(f"Erro na conexão: {e}", flush=True)
    finally:
        con.close()

def listar_agendamentos_medico(id_medico):
    """
    Busca todas as consultas de um médico
    """
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    try:
        # Faz um JOIN simples já que estão no mesmo DB para facilitar a visualização
        sql = """
            SELECT c.id_consulta, c.data_consulta, c.horario_consulta, c.status, p.nome as nome_paciente
            FROM consulta c
            JOIN paciente p ON c.id_paciente = p.id_usuario
            WHERE c.id_medico = %s
            ORDER BY c.data_consulta, c.horario_consulta
        """
        cursor.execute(sql, (id_medico,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar: {e}")
        return []
    finally:
        cursor.close()
        conn.close()



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