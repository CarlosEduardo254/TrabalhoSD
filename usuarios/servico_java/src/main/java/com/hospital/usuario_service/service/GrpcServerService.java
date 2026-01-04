package com.hospital.usuario_service.service;

import com.hospital.grpc.*;
import io.grpc.stub.StreamObserver;
import net.devh.boot.grpc.server.service.GrpcService;
import java.sql.*;

@GrpcService
public class GrpcServerService extends UsuarioServiceGrpc.UsuarioServiceImplBase {

    // Configurações de conexão com o MySQL do Docker
    private Connection getConnection() throws SQLException {
        String url = "jdbc:mysql://db:3306/hospital_db";
        String user = "root";
        String password = "123";
        return DriverManager.getConnection(url, user, password);
    }

    @Override
    public void criarUsuario(UsuarioRequest request, StreamObserver<UsuarioResponse> responseObserver) {
        String tipo = request.getTipo().toLowerCase();
        System.out.println("[DEBUG] CriarUsuario - Tipo Recebido: '" + tipo + "'");
        System.out.println("[DEBUG] CriarUsuario - Raw Request: " + request.toString());
        String sql = "";
        boolean sucesso = false;
        String mensagem = "";

        // LÓGICA DE DISTINÇÃO DE PERFIS
        switch (tipo) {
            case "paciente":
                sql = "INSERT INTO paciente (nome, problema, telefone, email, senha) VALUES (?, ?, ?, ?, ?)";
                break;
            case "medico":
                // info_extra(CRM)
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
            try (Connection conn = getConnection();
                    PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {

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
        boolean autenticado = false;
        String mensagem = "Usuário ou senha inválidos";
        String tipoUsuario = "";
        String nome = "";
        int idUsuario = 0;

        // Tabelas possíveis para login
        String[] tabelas = { "paciente", "medico", "recepcionista", "administradores" };

        try (Connection conn = getConnection()) {
            for (String tabela : tabelas) {
                // Query genérica para buscar em qualquer uma das tabelas
                String colNome = tabela.equals("medico") ? "nome_med" : "nome";
                String colId = tabela.equals("medico") ? "id_med" : "id_usuario"; // Médicos usam id_med

                String sql = "SELECT " + colNome + ", " + colId + " FROM " + tabela + " WHERE email = ? AND senha = ?";

                try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
                    pstmt.setString(1, request.getEmail());
                    pstmt.setString(2, request.getSenha());

                    try (ResultSet rs = pstmt.executeQuery()) {
                        if (rs.next()) {
                            autenticado = true;
                            mensagem = "Login realizado com sucesso";
                            tipoUsuario = tabela;
                            nome = rs.getString(colNome);
                            idUsuario = rs.getInt(colId);
                            break;
                        }
                    }
                }
            }
        } catch (SQLException e) {
            mensagem = "Erro interno no Banco: " + e.getMessage();
            e.printStackTrace();
        }

        LoginResponse response = LoginResponse.newBuilder()
                .setAutenticado(autenticado)
                .setMensagem(mensagem)
                .setTipoUsuario(tipoUsuario)
                .setNome(nome)
                .setIdUsuario(idUsuario)
                .build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void verificarUsuario(VerificarUsuarioRequest request,
            StreamObserver<VerificarUsuarioResponse> responseObserver) {
        boolean existe = false;
        int id = request.getId();

        // Verifica na tabela paciente
        String sql = "SELECT count(*) FROM paciente WHERE id_usuario = ?";
        try (Connection conn = getConnection(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    existe = rs.getInt(1) > 0;
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        VerificarUsuarioResponse response = VerificarUsuarioResponse.newBuilder()
                .setExiste(existe)
                .build();
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }
}