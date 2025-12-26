package com.hospital.usuario_service.model;

import jakarta.persistence.*;

@Entity // Diz: "Isso aqui representa uma tabela no banco"
@Table(name = "paciente") // Diz: "O nome da tabela no MySQL é 'paciente'"
public class Paciente {

    @Id // Diz: "Essa é a Chave Primária"
    @GeneratedValue(strategy = GenerationType.IDENTITY) // Diz: "O Banco gera o ID sozinho (Auto Increment)"
    @Column(name = "id_usuario") // O nome da coluna no banco é id_usuario
    private Long id;

    @Column(nullable = false) // Coluna obrigatória
    private String nome;

    @Column(nullable = false)
    private String problema;

    // Lembra que mudamos para String/Varchar no banco? Aqui reflete isso.
    @Column(nullable = false)
    private String telefone;

    @Column(nullable = false)
    private String email;

    @Column(nullable = false)
    private String senha;

    // --- Construtores, Getters e Setters (Obrigatórios para o Java funcionar) ---
    
    // Construtor vazio (O JPA exige isso)
    public Paciente() {}

    // Construtor cheio (Para facilitar nossa vida)
    public Paciente(String nome, String problema, String telefone, String email, String senha) {
        this.nome = nome;
        this.problema = problema;
        this.telefone = telefone;
        this.email = email;
        this.senha = senha;
    }

    // Getters (Para ler os dados) e Setters (Para gravar dados)
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getNome() { return nome; }
    public void setNome(String nome) { this.nome = nome; }

    public String getProblema() { return problema; }
    public void setProblema(String problema) { this.problema = problema; }

    public String getTelefone() { return telefone; }
    public void setTelefone(String telefone) { this.telefone = telefone; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getSenha() { return senha; }
    public void setSenha(String senha) { this.senha = senha; }
}
