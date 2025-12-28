import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

public class ServidorRMI implements IValidador {
    
    public ServidorRMI(){}

    @Override
    public boolean validarConvenio(String numeroCartao){
        System.out.println("[RMI] Validando cartão: " + numeroCartao);

        //Simulação: COnsideraremos se o número terminar com um número par como válido
        try{
            int ultimoDigito = Integer.parseInt(numeroCartao.substring(numeroCartao.length() - 1));
            boolean valido = (ultimoDigito % 2 == 0);

            System.out.println("[RMI] Resultado: " + (valido ? "APROVADO" : "REPROVADO"));
            return valido;
        }catch(Exception e){
            System.out.println("[RMI] Erro ao validar cartão: " + e.getMessage());
            return false;
        }
    }

    public static void main(String[] args) {
        try{
            // Criação da instância do servidor
            ServidorRMI servidor = new ServidorRMI();

            // Exportação do objeto para que ele possa ser chamado remotamente
            IValidador stub = (IValidador) UnicastRemoteObject.exportObject(servidor, 0); // 0 Oara usar uma porta anônima disponível

            // Criação do registro RMI na porta 1099(Padrão)
            Registry registry = LocateRegistry.createRegistry(1099);

            // Nome do serviço
            registry.bind("ValidadorService", stub);

            System.out.println("Serviço de Validação rodando na porta 1099");
        }catch(Exception e){
            System.err.println("[RMI] Erro ao iniciar o servidor: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
