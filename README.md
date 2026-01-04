# Sistema Hospitalar Distribuído

Este projeto implementa um sistema de gerenciamento hospitalar distribuído utilizando microsserviços.

## 🚀 Tecnologias

- **Backend**: Python (Flask, gRPC), Java (Spring Boot, gRPC, RMI)
- **Mensageria**: RabbitMQ
- **Banco de Dados**: MySQL
- **Containerização**: Docker & Docker Compose

## 🏛️ Arquitetura do Sistema

O sistema é composto por diversos microsserviços que se comunicam utilizando diferentes protocolos de redes, demonstrando a interoperabilidade entre tecnologias.

### 1. Serviço de Usuários (`usuarios/`)
- **Tecnologia**: Java (Spring Boot)
- **Comunicação Externa**: gRPC (Porta 50051)
- **Função**: Gerencia cadastro, login e verificação de pacientes, médicos e administradores.
- **Interface**: Possui um gateway Python (`interface_usuarios.py`) que expõe uma API REST (Porta 8083) para os clientes e converte para gRPC.

### 2. Serviço de Agendamento (`agendamento/`)
- **Tecnologia**: Python
- **Comunicação Externa**: Sockets TCP (Porta 5000)
- **Comunicação Interna**:
    - Consome o **Serviço de Usuários** via **gRPC** para verificar existência do paciente.
    - Publica mensagens no **RabbitMQ** para notificações.
    - Chama o **Adapter de Validação** via HTTP.
- **Interface**: Gateway Python (`interface_agendamento.py`) expõe API REST (Porta 8081) e converte para Sockets Raw.

### 3. Serviço de Validação de Convênio (`validacao/`)
- **Tecnologia**: Java (RMI Server)
- **Comunicação**: Java RMI (Porta 1099)
- **Adapter**: Um serviço intermediário em Python (`servico-adapter`) recebe requisições HTTP REST (Porta 8084) e invoca os métodos Java RMI (ponte HTTP <-> RMI).

### 4. Serviço de Notificações (`notificacoes/`)
- **Tecnologia**: Python
- **Comunicação**: Mensageria (RabbitMQ)
- **Função**: Worker que escuta a fila `email_queue` e simula o envio de e-mails de confirmação.

### 5. Clientes (`cliente/`)
- **Tecnologia**: Python (Scripts CLI)
- **Função**: Simulam as interações dos usuários finais consumindo as APIs REST (Gateways).

---

## 📋 Pré-requisitos

- Docker e Docker Compose instalados.
- Python 3.9+ (para rodar os clientes de teste).

## 🛠️ Como Executar

1.  **Subir os serviços**:
    Na raiz do projeto, execute:
    ```powershell
    docker-compose up --build
    ```
    Aguarde até que todos os serviços estejam rodando (status "Up" ou logs estabilizados). O serviço de notificações aguardará o RabbitMQ estar pronto automaticamente.

2.  **Parar os serviços**:
    ```powershell
    docker-compose down
    ```
    *Nota: O banco de dados é recriado a cada reinício (dados não persistentes).*

## 🧪 Como Testar (Clientes)

Os clientes de teste estão na pasta `cliente`. Recomenda-se criar um ambiente virtual (venv) para rodá-los.

### 1. Configurar Dependências do Cliente

```powershell
cd cliente
python -m venv .venv
# Ativar venv:
# Windows: .\.venv\Scripts\Activate
# Linux/Mac: source .venv/bin/activate
pip install requests
```

### 2. Fluxo de Teste Recomendado

Siga esta ordem para garantir que os dados existam (evitando erros de chave estrangeira):

#### A. Cadastrar Médico
Abra um terminal e rode:
```powershell
python cliente_medico.py
```
1.  Escolha **1. Cadastrar**.
2.  Preencha os dados (ex: CRM 123).
3.  **Anote o ID gerado** (provavelmente 1).
4.  Faça **Login** (Opção 2) para testar.
5.  Selecione **1. Ver Minha Agenda** (estará vazia inicialmente).

#### B. Cadastrar Paciente e Agendar
Abra **outro** terminal e rode:
```powershell
python cliente_paciente.py
```
1.  Escolha **1. Cadastrar**.
2.  Preencha os dados.
3.  Faça **Login** (Opção 2).
4.  Selecione **1. Agendar Consulta**.
5.  Informe o **ID do Médico** (1), Data (AAAA-MM-DD) e Horário.
6.  Você deve receber um **SUCESSO**.

#### C. Verificar Agendamento
Volte ao terminal do **cliente_medico.py**:
1.  Selecione novamente **1. Ver Minha Agenda**.
2.  A consulta agendada deve aparecer na lista.

## 🔍 Solução de Problemas

- **Erro de Conexão (WinError 10061)**: Os serviços não estão rodando. Verifique o Docker.
- **Login Falhou (Erro interno)**: Verifique se o banco de dados subiu corretamente. Tente reiniciar com `docker-compose down` e `up --build`.
- **Erro ao Agendar (Médico não existe)**: Certifique-se de cadastrar o médico ANTES de tentar agendar.
