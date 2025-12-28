from flask import Flask, request, jsonify
import grpc

# Importa os arquivos gerados pelo comando anterior
import usuario_pb2
import usuario_pb2_grpc

app = Flask(__name__)

def chamar_java_grpc(dados):
    # Endereço do Servidor Java
    CANAL_GRPC = 'localhost:9090'
    
    try:
        # 1. Cria o canal de comunicação com o Java
        channel = grpc.insecure_channel(CANAL_GRPC)
        stub = usuario_pb2_grpc.UsuarioServiceStub(channel)
        
        # 2. Monta o objeto que o Java espera (PacienteRequest)
        request_grpc = usuario_pb2.PacienteRequest(
            nome=dados.get('nome'),
            problema=dados.get('problema'),
            telefone=dados.get('telefone'),
            email=dados.get('email'),
            senha=dados.get('senha')
        )
        
        print(f"[Python] Enviando para o Java: {request_grpc.nome}")
        
        # 3. Chama a função remota (RPC)
        response = stub.CriarPaciente(request_grpc)
        
        return {
            "mensagem": response.mensagem,
            "id_gerado": response.id_gerado
        }
        
    except grpc.RpcError as e:
        print(f"[Erro gRPC] {e}")
        return {"erro": f"Falha na comunicação com Java: {e.code()}"}
    except Exception as e:
        return {"erro": str(e)}

@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    dados = request.json
    
    # Validação simples
    if not dados or 'nome' not in dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    
    # Chama a função que fala com o gRPC
    resposta_java = chamar_java_grpc(dados)
    
    return jsonify({
        "status_interface": "Processado pelo Python",
        "backend_java": resposta_java
    })

if __name__ == '__main__':
    # Roda na porta 8083
    print("--- Interface Usuários (Python) rodando em http://localhost:8083 ---")
    app.run(port=8083, debug=True)