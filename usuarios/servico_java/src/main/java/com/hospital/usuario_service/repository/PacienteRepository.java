package com.hospital.usuario_service.repository;

import com.hospital.usuario_service.model.Paciente;
import org.springframework.data.jpa.repository.JpaRepository;

// Interface que herda de JpaRepository.
// <Paciente, Long> significa: "Vou lidar com a tabela Paciente, e o ID dela é do tipo Long"
public interface PacienteRepository extends JpaRepository<Paciente, Long> {
    
}
