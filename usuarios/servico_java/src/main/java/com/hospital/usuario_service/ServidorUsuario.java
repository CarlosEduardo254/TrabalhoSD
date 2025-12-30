package com.hospital.usuario_service;

import com.hospital.usuario_service.service.GrpcServerService;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import java.io.IOException;

public class ServidorUsuario {
    public static void main(String[] args) throws IOException, InterruptedException {
        // Porta 9090 para o python conseguir conectar
        Server server = ServerBuilder.forPort(9090)
                .addService(new GrpcServerService())
                .build();

        System.out.println("--- Servidor Java gRPC rodando na porta 9090 ---");
        server.start();
        server.awaitTermination();
    }
}