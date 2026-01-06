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
        int idGerado = 0;

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

                    // Captura o ID gerado
                    try (ResultSet generatedKeys = pstmt.getGeneratedKeys()) {
                        if (generatedKeys.next()) {
                            idGerado = generatedKeys.getInt(1);
                        }
                    }
                }
            } catch (SQLException e) {
                mensagem = "Erro no Banco: " + e.getMessage();
                e.printStackTrace();
            }
        }

        UsuarioResponse response = UsuarioResponse.newBuilder()
                .setMensagem(mensagem)
                .setSucesso(sucesso)
                .setIdGerado(idGerado)
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
                String colId;
                switch (tabela) {
                    case "medico":
                        colId = "id_med";
                        break;
                    case "recepcionista":
                        colId = "id_recep";
                        break;
                    case "administradores":
                        colId = "id_adm";
                        break;
                    default:
                        colId = "id_usuario"; // paciente
                }
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

    @Override
    public void atualizarUsuario(AtualizarUsuarioRequest request, StreamObserver<UsuarioResponse> responseObserver) {
        String tipo = request.getTipo().toLowerCase();
        int id = request.getId();
        boolean sucesso = false;
        String mensagem = "";

        // Colunas de ID por tabela
        String colId;
        String tabela;
        String colNome = "nome";
        String colInfoExtra = "";

        switch (tipo) {
            case "paciente":
                tabela = "paciente";
                colId = "id_usuario";
                colInfoExtra = "problema";
                break;
            case "medico":
                tabela = "medico";
                colId = "id_med";
                colNome = "nome_med";
                colInfoExtra = "crm";
                break;
            case "recepcionista":
                tabela = "recepcionista";
                colId = "id_recep";
                break;
            case "admin":
                tabela = "administradores";
                colId = "id_adm";
                break;
            default:
                mensagem = "Tipo de usuário inválido!";
                UsuarioResponse response = UsuarioResponse.newBuilder()
                        .setMensagem(mensagem)
                        .setSucesso(false)
                        .setIdGerado(0)
                        .build();
                responseObserver.onNext(response);
                responseObserver.onCompleted();
                return;
        }

        // Construir query dinamicamente (só atualiza campos não vazios)
        StringBuilder sql = new StringBuilder("UPDATE " + tabela + " SET ");
        java.util.List<String> valores = new java.util.ArrayList<>();

        if (!request.getNome().isEmpty()) {
            sql.append(colNome + " = ?, ");
            valores.add(request.getNome());
        }
        if (!request.getTelefone().isEmpty()) {
            sql.append("telefone = ?, ");
            valores.add(request.getTelefone());
        }
        if (!request.getEmail().isEmpty()) {
            sql.append("email = ?, ");
            valores.add(request.getEmail());
        }
        if (!request.getSenha().isEmpty()) {
            sql.append("senha = ?, ");
            valores.add(request.getSenha());
        }
        if (!colInfoExtra.isEmpty() && !request.getInfoExtra().isEmpty()) {
            sql.append(colInfoExtra + " = ?, ");
            valores.add(request.getInfoExtra());
        }

        // Se nenhum campo foi preenchido
        if (valores.isEmpty()) {
            mensagem = "Nenhum campo para atualizar foi informado";
            UsuarioResponse response = UsuarioResponse.newBuilder()
                    .setMensagem(mensagem)
                    .setSucesso(false)
                    .setIdGerado(id)
                    .build();
            responseObserver.onNext(response);
            responseObserver.onCompleted();
            return;
        }

        // Remove a última vírgula e adiciona WHERE
        sql.setLength(sql.length() - 2);
        sql.append(" WHERE " + colId + " = ?");

        try (Connection conn = getConnection();
                PreparedStatement pstmt = conn.prepareStatement(sql.toString())) {

            int index = 1;
            for (String valor : valores) {
                pstmt.setString(index++, valor);
            }
            pstmt.setInt(index, id);

            int affectedRows = pstmt.executeUpdate();
            if (affectedRows > 0) {
                sucesso = true;
                mensagem = "Usuário atualizado com sucesso";
            } else {
                mensagem = "Nenhum usuário encontrado com o ID informado";
            }
        } catch (SQLException e) {
            mensagem = "Erro no Banco: " + e.getMessage();
            e.printStackTrace();
        }

        UsuarioResponse response = UsuarioResponse.newBuilder()
                .setMensagem(mensagem)
                .setSucesso(sucesso)
                .setIdGerado(id)
                .build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void deletarUsuario(DeletarUsuarioRequest request, StreamObserver<UsuarioResponse> responseObserver) {
        String tipo = request.getTipo().toLowerCase();
        int id = request.getId();
        String sql = "";
        boolean sucesso = false;
        String mensagem = "";

        switch (tipo) {
            case "paciente":
                sql = "DELETE FROM paciente WHERE id_usuario = ?";
                break;
            case "medico":
                sql = "DELETE FROM medico WHERE id_med = ?";
                break;
            case "recepcionista":
                sql = "DELETE FROM recepcionista WHERE id_recep = ?";
                break;
            case "admin":
                sql = "DELETE FROM administradores WHERE id_adm = ?";
                break;
            default:
                mensagem = "Tipo de usuário inválido!";
        }

        if (!sql.isEmpty()) {
            try (Connection conn = getConnection();
                    PreparedStatement pstmt = conn.prepareStatement(sql)) {
                pstmt.setInt(1, id);

                int affectedRows = pstmt.executeUpdate();
                if (affectedRows > 0) {
                    sucesso = true;
                    mensagem = "Usuário deletado com sucesso";
                } else {
                    mensagem = "Nenhum usuário encontrado com o ID informado";
                }
            } catch (SQLException e) {
                mensagem = "Erro no Banco: " + e.getMessage();
                e.printStackTrace();
            }
        }

        UsuarioResponse response = UsuarioResponse.newBuilder()
                .setMensagem(mensagem)
                .setSucesso(sucesso)
                .setIdGerado(0)
                .build();

        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void listarUsuarios(ListarUsuariosRequest request, StreamObserver<ListarUsuariosResponse> responseObserver) {
        String tipoFiltro = request.getTipo().toLowerCase();
        ListarUsuariosResponse.Builder responseBuilder = ListarUsuariosResponse.newBuilder();

        try (Connection conn = getConnection()) {
            // Lista pacientes
            if (tipoFiltro.equals("paciente") || tipoFiltro.equals("todos")) {
                String sql = "SELECT id_usuario, nome, email, telefone, problema FROM paciente";
                try (PreparedStatement pstmt = conn.prepareStatement(sql);
                        ResultSet rs = pstmt.executeQuery()) {
                    while (rs.next()) {
                        UsuarioInfo usuario = UsuarioInfo.newBuilder()
                                .setId(rs.getInt("id_usuario"))
                                .setNome(rs.getString("nome"))
                                .setEmail(rs.getString("email"))
                                .setTelefone(rs.getString("telefone"))
                                .setTipo("paciente")
                                .setInfoExtra(rs.getString("problema"))
                                .build();
                        responseBuilder.addUsuarios(usuario);
                    }
                }
            }

            // Lista médicos
            if (tipoFiltro.equals("medico") || tipoFiltro.equals("todos")) {
                String sql = "SELECT id_med, nome_med, email, telefone, crm FROM medico";
                try (PreparedStatement pstmt = conn.prepareStatement(sql);
                        ResultSet rs = pstmt.executeQuery()) {
                    while (rs.next()) {
                        UsuarioInfo usuario = UsuarioInfo.newBuilder()
                                .setId(rs.getInt("id_med"))
                                .setNome(rs.getString("nome_med"))
                                .setEmail(rs.getString("email"))
                                .setTelefone(rs.getString("telefone"))
                                .setTipo("medico")
                                .setInfoExtra(rs.getString("crm") != null ? rs.getString("crm") : "")
                                .build();
                        responseBuilder.addUsuarios(usuario);
                    }
                }
            }

            // Lista recepcionistas
            if (tipoFiltro.equals("recepcionista") || tipoFiltro.equals("todos")) {
                String sql = "SELECT id_recep, nome, email, telefone FROM recepcionista";
                try (PreparedStatement pstmt = conn.prepareStatement(sql);
                        ResultSet rs = pstmt.executeQuery()) {
                    while (rs.next()) {
                        UsuarioInfo usuario = UsuarioInfo.newBuilder()
                                .setId(rs.getInt("id_recep"))
                                .setNome(rs.getString("nome"))
                                .setEmail(rs.getString("email"))
                                .setTelefone(rs.getString("telefone"))
                                .setTipo("recepcionista")
                                .setInfoExtra("")
                                .build();
                        responseBuilder.addUsuarios(usuario);
                    }
                }
            }

            // Lista administradores
            if (tipoFiltro.equals("admin") || tipoFiltro.equals("administradores") || tipoFiltro.equals("todos")) {
                String sql = "SELECT id_adm, nome, email, telefone FROM administradores";
                try (PreparedStatement pstmt = conn.prepareStatement(sql);
                        ResultSet rs = pstmt.executeQuery()) {
                    while (rs.next()) {
                        UsuarioInfo usuario = UsuarioInfo.newBuilder()
                                .setId(rs.getInt("id_adm"))
                                .setNome(rs.getString("nome"))
                                .setEmail(rs.getString("email"))
                                .setTelefone(rs.getString("telefone"))
                                .setTipo("admin")
                                .setInfoExtra("")
                                .build();
                        responseBuilder.addUsuarios(usuario);
                    }
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        responseObserver.onNext(responseBuilder.build());
        responseObserver.onCompleted();
    }

}