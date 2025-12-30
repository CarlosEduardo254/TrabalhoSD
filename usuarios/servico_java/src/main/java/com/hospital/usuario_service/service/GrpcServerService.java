package com.hospital.usuario_service.service;

import com.hospital.grpc.*;
import io.grpc.stub.StreamObserver;
import net.devh.boot.grpc.server.service.GrpcService;
import java.sql.*;

@GrpcService
public class GrpcServerService extends UsuarioServiceGrpc.UsuarioServiceImplBase {

    // Configurações de conexão com o MySQL do Docker
    private Connection getConnection() throws SQLException {
        String url = "jdbc:mysql://localhost:3307/hospital_db"; // Certifica que o nome do banco está correto
        String user = "root"; 
        String password = "123"; 
        return DriverManager.getConnection(url, user, password);
    }

    @Override
    public void criarUsuario(UsuarioRequest request, StreamObserver<UsuarioResponse> responseObserver) {
        String tipo = request.getTipo().toLowerCase();
        String sql = "";
        boolean sucesso = false;
        String mensagem = "";

        // LÓGICA DE DISTINÇÃO DE PERFIS
        switch (tipo) {
            case "paciente":
                sql = "INSERT INTO paciente (nome, problema, telefone, email, senha) VALUES (?, ?, ?, ?, ?)";
                break;
            case "medico":
                //info_extra(CRM)
                sql = "INSERT INTO medico (nome_med, especialidade, crm, telefone, email, senha) VALUES (?, 'Geral', ?, ?, ?, ?)";
                break;
            case "recepcionista":
                sql = "INSERT INTO recepcionista (nome, telefone, email, senha) VALUES (?, ?, ?, ?)";
                break;
            case "admin":
                sql = "INSERT INTO administradores (nome, telefone, email, senha) VALUES (?, ?, ?, ?)";
                break;
            default:
                mensagem = "Tipo de usuário inválido!";
        }

        if (!sql.isEmpty()) {
            try (Connection conn = getConnection(); PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
                
                // Preenchimento dos campos baseado na tabela
                if (tipo.equals("paciente") || tipo.equals("medico")) {
                    pstmt.setString(1, request.getNome());
                    pstmt.setString(2, request.getInfoExtra()); // Problema ou CRM
                    pstmt.setString(3, request.getTelefone());
                    pstmt.setString(4, request.getEmail());
                    pstmt.setString(5, request.getSenha());
                } else {
                    // Recepcionista e Admin não têm o campo info_extra(no caso o problema ou CRM)
                    pstmt.setString(1, request.getNome());
                    pstmt.setString(2, request.getTelefone());
                    pstmt.setString(3, request.getEmail());
                    pstmt.setString(4, request.getSenha());
                }

                int affectedRows = pstmt.executeUpdate();
                if (affectedRows > 0) {
                    sucesso = true;
                    mensagem = "Cadastro de " + tipo + " realizado com sucesso";
                }
            } catch (SQLException e) {
                mensagem = "Erro no Banco: " + e.getMessage();
                e.printStackTrace();
            }
        }

        UsuarioResponse response = UsuarioResponse.newBuilder()
                .setMensagem(mensagem)
                .setSucesso(sucesso)
                .setIdGerado(sucesso ? 1 : 0)
                .build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void login(LoginRequest request, StreamObserver<LoginResponse> responseObserver) {
        //teste de login, mais tarde temos que fazer uma busca usando o "select" nas tabelas do bd
        LoginResponse response = LoginResponse.newBuilder()
                .setAutenticado(true)
                .setMensagem("Login simulado com sucesso")
                .setTipoUsuario("paciente")
                .setNome("Teste")
                .build();
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }
}