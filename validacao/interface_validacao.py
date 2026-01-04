from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

def chamar_java_rmi(numero_cartao):
    # Guardar o caminho onde estão os arquivos Java
    #CAMINHO_JAVA = "C:\\dev\\TrabalhoSD\\validacao\\src"
    CAMINHO_JAVA = os.path.join(os.getcwd(), 'validacao', 'src')

    try:
        processo = subprocess.run(
            ['java', '-cp', '.', 'ClienteRMI', str(numero_cartao)],
            cwd=CAMINHO_JAVA, #Define onde o comando vai rodar
            capture_output=True, #Captura a saída do comando
            text=True, #Garante que a saída seja tratada como texto
            check=True # Se crashar lança uma exceção
        )

        # Pega a saída e remove os espaços em branco
        resposta = processo.stdout.strip()
        return resposta
    except subprocess.CalledProcessError as e:
        return f"Erro na execução do Java: {e.stderr}"
    except Exception as e:
        return f"Erro do Python: {str(e)}"

@app.route('/validar_convenio', methods=['POST'])
def validar_convenio():
    dados = request.json

    if not dados or 'numero_cartao' not in dados:
        return jsonify({"erro": "Número do cartão não informado"}), 400

    cartao = dados['numero_cartao']
    print(f"[Python] Validando cartão: {cartao}")

    # Chama o Java para validar
    resultado_rmi = chamar_java_rmi(cartao)

    return jsonify({
        "cartao": cartao,
        "status_convenio": resultado_rmi,
        "origem": "Processado via Java RMI"
    })

if __name__ == '__main__':
    # Porta 8084 para não conflitar com Agendamento(8081) e Usuários(8083) e Web(8082)
    print("--- Interface Validação (Python) rodando em http://localhost:8084 ---")
    app.run(host='0.0.0.0', port=8084, debug=True)
