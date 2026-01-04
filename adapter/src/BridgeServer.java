import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class BridgeServer {

    public static void main(String[] args) {
        try {
            // 1. Conecta no RMI do serviço de validação
            // Tenta conectar repetidamente caso o serviço de validação demore a subir
            Registry registry = null;
            IValidador validador = null;
            
            System.out.println("[Bridge] Aguardando serviço RMI...");
            while (validador == null) {
                try {
                    // 'servico_validacao' é o nome do container no Docker Compose
                    registry = LocateRegistry.getRegistry("servico_validacao", 1099);
                    validador = (IValidador) registry.lookup("ValidadorService");
                } catch (Exception e) {
                    Thread.sleep(2000); // Espera 2 segundos
                }
            }
            System.out.println("[Bridge] Conectado ao RMI com sucesso!");

            // 2. Inicia o Servidor Socket para o Python
            ServerSocket serverSocket = new ServerSocket(7000);
            System.out.println("[Bridge] Rodando Socket na porta 7000...");

            while (true) {
                Socket clientSocket = serverSocket.accept();
                handleClient(clientSocket, validador);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void handleClient(Socket socket, IValidador validador) {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {

            // Lê o JSON enviado pelo Python
            String jsonInput = in.readLine();
            System.out.println("[Bridge] Recebido: " + jsonInput);

            // Parser manual de JSON simples para pegar o id_paciente/id_consulta
            // Assumindo que o Python manda algo como {"id_paciente": "123", ...}
            // Para simplificar, vamos extrair apenas o número para validação.
            // No seu ServidorRMI original, a lógica era: (ultimoDigito % 2 == 0)
            
            // Vamos extrair o valor do "id_paciente" do JSON para usar como número do cartão
            String numeroParaValidar = "0"; 
            if (jsonInput.contains("id_paciente")) {
                 // Extração simples de string (melhor usar lib GSON em produção, mas aqui vai sem lib externa)
                 String[] parts = jsonInput.split("\"id_paciente\":");
                 if (parts.length > 1) {
                     String valor = parts[1].split(",")[0].trim().replace("\"", "").replace("}", "");
                     numeroParaValidar = valor;
                 }
            }

            // 3. Chama o RMI
            boolean aprovado = validador.validarConvenio(numeroParaValidar);

            // 4. Devolve JSON para o Python
            String jsonResponse = "{\"aprovado\": " + aprovado + "}";
            out.println(jsonResponse);

        } catch (Exception e) {
            System.err.println("Erro no processamento: " + e.getMessage());
        }
    }
}