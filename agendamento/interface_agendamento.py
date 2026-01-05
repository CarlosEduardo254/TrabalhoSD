from flask import Flask, request, jsonify # Flask cria o servidor web
import socket
import json
import pika

app = Flask(__name__) # Inicializa o app Flask

#Função que envia uma mensagem para o RabbitMQ
def enviar_notificacao_fila(texto_msg):
    try:
        # Conexão com o RabbitMQ
        credentials = pika.PlainCredentials('user', 'password')
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue='email_queue') # Para garantir que a fila existe

        channel.basic_publish(exchange='', routing_key='email_queue', body=texto_msg)
        print(f"[RabbitMQ] Enviado: {texto_msg}")
        connection.close()
    except Exception as e:
        print(f"[RabbitMQ] Erro ao enviar mensagem: {e}")


import os
# Função que age como CLIENTE do Socket (igual ao curl ou browser)
def enviar_socket(dados_dict):
    HOST = os.getenv('SOCKET_HOST', '127.0.0.1')
    PORT = 5000        
    
    try:
        # Cria o socket
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Tenta conectar no servidor (servico_agendamento.py)
        tcp.connect((HOST, PORT))
        
        # Converte o dicionário python em texto JSON
        msg = json.dumps(dados_dict)
        # Manda os dados
        tcp.send(msg.encode('utf-8'))
        
        # Fica esperando a resposta (até 4096 bytes)
        resposta = tcp.recv(4096).decode('utf-8')
        tcp.close() # Fecha a conexão
        return resposta
    except Exception as e:
        return f"Erro de comunicação com o Serviço Socket: {e}"

# Define a rota HTTP (o endpoint que você chama no Postman)
@app.route('/agendar', methods=['POST'])
def rota_agendar():
    # Pega o JSON que veio no corpo da requisição HTTP
    dados = request.json
    
    # Validação básica
    if not dados:
        return jsonify({"erro": "Sem dados"}), 400
    
    # Adiciona a ação para o socket saber o que fazer
    dados['acao'] = 'agendar'

    # A MÁGICA: A interface não salva nada. Ela repassa a bola pro Socket.
    resposta_servico = enviar_socket(dados)

    if "SUCESSO" in resposta_servico:
        msg_notificacao = f"Agendamento confirmado para Médico {dados['id_medico']} na data {dados['data']} às {dados['horario']}"
        enviar_notificacao_fila(msg_notificacao)
    
    # Retorna para o usuário (navegador/postman) o que o Socket respondeu
    return jsonify({
        "status": "Processado",
        "resposta_do_servico": resposta_servico
    })

@app.route('/listar_agenda', methods=['POST'])
def rota_listar_agenda():
    dados = request.json
    if not dados or 'id_medico' not in dados:
        return jsonify({"erro": "ID do médico obrigatório"}), 400

    dados['acao'] = 'listar_medico'
    
    # Chama o socket (que agora retorna um JSON string com a lista)
    resposta_servico = enviar_socket(dados)
    
    try:
        # O socket retorna uma string, se for lista JSON válida, convertemos de volta
        lista = json.loads(resposta_servico)
        return jsonify(lista)
    except:
        # Se deu erro ou retornou texto puro
        return jsonify({"erro": resposta_servico})


@app.route('/listar_meus_agendamentos', methods=['POST'])
def rota_listar_meus_agendamentos():
    dados = request.json
    if not dados or 'id_paciente' not in dados:
        return jsonify({"erro": "ID do paciente obrigatório"}), 400
    
    dados['acao'] = 'listar_paciente'
    resposta_servico = enviar_socket(dados)
    
    try:
        lista = json.loads(resposta_servico)
        return jsonify(lista)
    except:
        return jsonify({"erro": resposta_servico})

@app.route('/cancelar_agendamento', methods=['DELETE'])
def rota_cancelar_agendamento():
    dados = request.json
    if not dados or 'id_consulta' not in dados:
        return jsonify({"erro": "ID da consulta obrigatório"}), 400
    
    dados['acao'] = 'cancelar'
    resposta_servico = enviar_socket(dados)
    
    try:
        resultado = json.loads(resposta_servico)
        return jsonify(resultado)
    except:
        return jsonify({"erro": resposta_servico})

@app.route('/pagar_consulta', methods=['POST'])
def rota_pagar_consulta():
    dados = request.json
    if not dados or 'id_consulta' not in dados:
        return jsonify({"erro": "ID da consulta obrigatório"}), 400
    
    dados['acao'] = 'pagar'
    resposta_servico = enviar_socket(dados)
    
    try:
        resultado = json.loads(resposta_servico)
        return jsonify(resultado)
    except:
        return jsonify({"erro": resposta_servico})

if __name__ == '__main__':
    # Roda o servidor web na porta 8081
    app.run(host='0.0.0.0', port=8081, debug=True)