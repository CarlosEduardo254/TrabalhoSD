import java.rmi.Remote;
import java.rmi.RemoteException;

public interface IValidador extends Remote {
    boolean validarConvenio(String numeroCartao) throws RemoteException;
}