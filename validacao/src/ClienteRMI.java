import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class ClienteRMI {
    public static void main(String[] args) {
        try {

            if (args.length == 0) {
                System.out.println("ERRO: Informe o número do cartão");
                return;
            }

            String numeroCartao = args[0];
            String host = (args.length > 1) ? args[1] : "localhost"; // Pega host do argumento ou default

            // Procura o registro RMI
            Registry registry = LocateRegistry.getRegistry(host, 1099);
            // Busca serviço
            IValidador validador = (IValidador) registry.lookup("ValidadorService");

            boolean valido = validador.validarConvenio(numeroCartao);

            // Impressão para o Pythn ler de forma facilitada
            System.out.print((valido ? "VALIDO" : "INVALIDO"));

        } catch (Exception e) {
            System.err.println("[RMI] Erro ao iniciar o cliente: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
