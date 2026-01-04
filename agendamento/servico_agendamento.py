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
    paciente_existe = verificar_paciente_grpc(dados["id_paciente"])
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

def validar_consulta_rmi(id_paciente, id_consulta) -> bool:
    """
    Chama o Adapter via HTTP, que por sua vez chama o Java RMI
    """
    try:
        # Pega a URL do Adapter do ambiente docker
        adapter_host = os.getenv('ADAPTER_HOST', 'servico-adapter')
        url = f"http://{adapter_host}:8084/validar_convenio"
        
        # Simulação: O cartão do convênio poderia vir no payload. 
        # Como não vem no JSON original, vamos simular que o ID do paciente é usado p/ buscar o cartão
        # ou vamos passar um dummy para validar.
        # REGRA DE NEGOCIO: Validamos se o ID do paciente é par/impar como regra do RMI lá no Java
        numero_cartao_simulado = f"1000{id_paciente}" 
        
        payload = {"numero_cartao": numero_cartao_simulado}
        
        print(f"[Orchestrator] Chamando Adapter em {url} com {payload}", flush=True)
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            dados = response.json()
            # O Java RMI retorna "VALIDO" ou "INVALIDO"
            status_rmi = dados.get("status_convenio", "").strip()
            return status_rmi == "VALIDO"
            
        print(f"[Orchestrator] Erro no Adapter: {response.text}")
        return False

    except Exception as e:
        print(f"[RMI/Adapter] Erro ao validar consulta: {e}")
        return False

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