from flask import Flask, request, jsonify # Flask cria o servidor web
import socket
import json

app = Flask(__name__) # Inicializa o app Flask

# Função que age como CLIENTE do Socket (igual ao curl ou browser)
def enviar_socket(dados_dict):
    HOST = '127.0.0.1' 
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
    
    # A MÁGICA: A interface não salva nada. Ela repassa a bola pro Socket.
    resposta_servico = enviar_socket(dados)
    
    # Retorna para o usuário (navegador/postman) o que o Socket respondeu
    return jsonify({
        "status": "Processado",
        "resposta_do_servico": resposta_servico
    })

if __name__ == '__main__':
    # Roda o servidor web na porta 8081
    app.run(port=8081, debug=True)