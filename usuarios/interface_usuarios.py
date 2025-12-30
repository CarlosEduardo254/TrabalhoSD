from flask import Flask, request, jsonify
import grpc
import usuario_pb2
import usuario_pb2_grpc

app = Flask(__name__)

def obter_stub():
    channel = grpc.insecure_channel('localhost:9090')
    return usuario_pb2_grpc.UsuarioServiceStub(channel)

@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    dados = request.json
    stub = obter_stub()
    
    # Monta a requisição com o campo 'tipo' (paciente, medico, etc)
    request_grpc = usuario_pb2.UsuarioRequest(
        nome=dados.get('nome'),
        email=dados.get('email'),
        senha=dados.get('senha'),
        telefone=dados.get('telefone'),
        tipo=dados.get('tipo', 'paciente').lower(),
        info_extra=dados.get('info_extra', '') # Problema ou CRM
    )
    
    try:
        response = stub.CriarUsuario(request_grpc)
        return jsonify({"mensagem": response.mensagem, "id": response.id_gerado})
    except grpc.RpcError as e:
        return jsonify({"erro": str(e.code())}), 500

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    stub = obter_stub()
    
    request_login = usuario_pb2.LoginRequest(
        email=dados.get('email'),
        senha=dados.get('senha')
    )
    
    try:
        response = stub.Login(request_login)
        if response.autenticado:
            return jsonify({
                "status": "sucesso",
                "perfil": response.tipo_usuario,
                "nome": response.nome,
                "id": response.id_usuario
            })
        else:
            return jsonify({"status": "erro", "mensagem": response.mensagem}), 401
    except grpc.RpcError as e:
        return jsonify({"erro": str(e.code())}), 500

if __name__ == '__main__':
    app.run(port=8083, debug=True)