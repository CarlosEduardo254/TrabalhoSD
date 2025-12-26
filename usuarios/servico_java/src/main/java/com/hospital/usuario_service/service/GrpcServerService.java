package com.hospital.usuario_service.service;

import com.hospital.grpc.UsuarioServiceGrpc;
import com.hospital.grpc.PacienteRequest;
import com.hospital.grpc.PacienteResponse;

import com.hospital.usuario_service.model.Paciente;
import com.hospital.usuario_service.repository.PacienteRepository;
import io.grpc.stub.StreamObserver;
import net.devh.boot.grpc.server.service.GrpcService;
import org.springframework.beans.factory.annotation.Autowired;

@GrpcService
public class GrpcServerService extends UsuarioServiceGrpc.UsuarioServiceImplBase {

    @Autowired
    private PacienteRepository pacienteRepository;

    @Override
    public void criarPaciente(PacienteRequest request, StreamObserver<PacienteResponse> responseObserver) {

        System.out.println(">>> gRPC: Recebido pedido para criar: " + request.getNome());

        // Converter o objeto do gRPC (Proto) para o objeto do Banco (Entity)
        Paciente novoPaciente = new Paciente(
                request.getNome(),
                request.getProblema(),
                request.getTelefone(),
                request.getEmail(),
                request.getSenha());

        // Salvar no Banco de Dados
        Paciente pacienteSalvo = pacienteRepository.save(novoPaciente);

        System.out.println(">>> gRPC: Salvo com sucesso. ID gerado: " + pacienteSalvo.getId());

        // Montar a resposta
        PacienteResponse resposta = PacienteResponse.newBuilder()
                .setMensagem("SUCESSO: Paciente cadastrado via Java/gRPC!")
                .setIdGerado(pacienteSalvo.getId().intValue())
                .build();

        responseObserver.onNext(resposta);
        responseObserver.onCompleted();
    }
}