# Sistema Hospitalar Distribuído

Este projeto implementa um sistema de gerenciamento hospitalar distribuído utilizando microsserviços, desenvolvido para a disciplina de Sistemas Distribuídos 2025.2.

## Tecnologias

- **Backend**: Python (Flask, gRPC), Java (Spring Boot, gRPC, RMI)
- **Mensageria**: RabbitMQ
- **Banco de Dados**: MySQL
- **Containerização**: Docker & Docker Compose

## Arquitetura do Sistema

O sistema é composto por diversos microsserviços que se comunicam utilizando diferentes protocolos de redes, demonstrando a interoperabilidade entre tecnologias.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTES                                    │
│  (admin.py, medico.py, paciente.py, recepcionista.py, cliente_*.py)     │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ HTTP REST
        ┌───────────────────────┼───────────────────────────┐
        ▼                       ▼                           ▼
┌───────────────┐    ┌──────────────────┐         ┌────────────────┐
│  Interface    │    │    Interface     │         │   RabbitMQ     │
│   Usuários    │    │   Agendamento    │         │   (5672)       │
│   (8083)      │    │     (8081)       │         └───────┬────────┘
└───────┬───────┘    └────────┬─────────┘                 │
        │ gRPC                │ TCP Socket                │
        ▼                     ▼                           ▼
┌───────────────┐    ┌──────────────────┐         ┌────────────────┐
│   Serviço     │◄───│     Serviço      │────────►│   Serviço      │
│   Usuários    │gRPC│   Agendamento    │ Publica │  Notificações  │
│   (50051)     │    │     (5000)       │         └────────────────┘
└───────┬───────┘    └────────┬─────────┘
        │                     │ HTTP
        ▼                     ▼
┌───────────────┐    ┌──────────────────┐
│    MySQL      │    │  Serviço Adapter │───► Serviço Validação
│   (3307)      │    │     (8084)       │ RMI     (Java RMI 1099)
└───────────────┘    └──────────────────┘
```

### Serviços

| Serviço | Tecnologia | Porta | Protocolo | Função |
|---------|------------|-------|-----------|--------|
| **Serviço de Usuários** | Java (Spring Boot) | 50051 | gRPC | Cadastro, login e verificação de usuários |
| **Interface Usuários** | Python (Flask) | 8083 | REST → gRPC | Gateway HTTP para o serviço de usuários |
| **Serviço de Agendamento** | Python | 5000 | TCP Socket | Gerencia consultas médicas |
| **Interface Agendamento** | Python (Flask) | 8081 | REST → Socket | Gateway HTTP para o serviço de agendamento |
| **Serviço de Validação** | Java | 1099 | RMI | Valida convênios médicos |
| **Serviço Adapter** | Python + Java | 8084 | HTTP → RMI | Ponte entre HTTP e RMI |
| **Serviço de Notificações** | Python | - | RabbitMQ | Processa fila de emails |
| **RabbitMQ** | - | 5672/15672 | AMQP | Mensageria assíncrona |
| **MySQL** | - | 3307 | SQL | Banco de dados |

---

## Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.9+ (para rodar os clientes de teste)
- `requests` (biblioteca Python para os clientes)

## Como Executar

### 1. Subir os Serviços

Na raiz do projeto, execute:
```powershell
docker-compose up --build
```

Para rodar em background:
```powershell
docker-compose up --build -d
```

Aguarde até que todos os serviços estejam rodando. Para verificar:
```powershell
docker-compose ps
```

### 2. Parar os Serviços

```powershell
docker-compose down
```

**Para limpar o banco de dados e recomeçar:**
```powershell
docker-compose down -v
docker-compose up --build
```

---

## Scripts Cliente

Os scripts cliente estão na pasta `cliente/`. Existem dois tipos:

### Scripts CLI (Linha de Comando)

Scripts para execução direta com argumentos:

| Script | Descrição |
|--------|-----------|
| `admin.py` | Gerenciamento de administradores e listagem de usuários |
| `medico.py` | Cadastro de médicos e visualização de agenda |
| `paciente.py` | Agendamento de consultas e gerenciamento de conta |
| `recepcionista.py` | Agendamento, cancelamento e registro de pagamentos |

### Scripts Interativos (Menu)

Scripts com interface de menu interativo:

| Script | Descrição |
|--------|-----------|
| `cliente_admin.py` | Menu interativo para administradores |
| `cliente_medico.py` | Menu interativo para médicos |
| `cliente_paciente.py` | Menu interativo para pacientes |
| `cliente_recepcionista.py` | Menu interativo para recepcionistas |

### Scripts Utilitários

| Script | Descrição |
|--------|-----------|
| `cadastrar_todos.py` | Cadastra automaticamente dados de teste (10 de cada tipo de usuário, agendamentos e pagamentos) |

---

## Exemplos de Uso (Scripts CLI)

### Configurar Ambiente
```powershell
cd cliente
python -m venv .venv
.\.venv\Scripts\Activate
pip install requests
```

### Paciente
```powershell
# Criar paciente
python paciente.py criar "José Silva" "jose@email.com" "senha123" "88999991111" "Dor de cabeça"

# Login
python paciente.py login "jose@email.com" "senha123"

# Agendar consulta (convênio)
python paciente.py agendar 1 1 "2026-01-15" "09:00:00"

# Agendar consulta (particular)
python paciente.py particular 1 1 "2026-01-15" "10:00:00"

# Listar consultas
python paciente.py listar 1

# Cancelar consulta
python paciente.py cancelar 1 5
```

### Médico
```powershell
# Criar médico
python medico.py criar "Dr. João Silva" "joao@hospital.com" "senha123" "88999991111" "12345-CE"

# Login
python medico.py login "joao@hospital.com" "senha123"

# Ver agenda
python medico.py agenda 1
```

### Recepcionista
```powershell
# Criar recepcionista
python recepcionista.py criar "Fernanda Lima" "fernanda@hospital.com" "recep123" "88999993331"

# Agendar para paciente
python recepcionista.py agendar 1 1 "2026-01-15" "10:00:00"

# Registrar pagamento
python recepcionista.py pagar 1 200.00 "Cartão de Crédito"

# Cancelar consulta
python recepcionista.py cancelar 5
```

### Administrador
```powershell
# Criar admin
python admin.py criar "Admin Sistema" "admin@hospital.com" "admin123" "88999990000"

# Listar todos os usuários
python admin.py listar_todos
```

---

## Tipos de Consulta e Pagamento

### Tipos de Consulta

| Tipo | Descrição | Status Inicial |
|------|-----------|----------------|
| **Convênio** | Validação automática pelo sistema | CONFIRMADA (ID par) ou PENDENTE (ID ímpar) |
| **Particular** | Sem convênio, requer pagamento | Sempre PENDENTE até pagar |

### Formas de Pagamento

- `Dinheiro`
- `PIX`
- `Cartão de Crédito`
- `Cartão de Débito`

> **Nota:** Apenas a **RECEPÇÃO** pode registrar pagamentos de consultas!

---

## Solução de Problemas

| Erro | Causa | Solução |
|------|-------|---------|
| `WinError 10061` | Serviços não estão rodando | Verifique se os containers estão ativos com `docker-compose ps` |
| Login falhou (erro interno) | Banco de dados não subiu | Reinicie com `docker-compose down` e `up --build` |
| Erro ao agendar (médico não existe) | Médico não cadastrado | Cadastre o médico antes de agendar |
| Erro de chave estrangeira | Dados dependentes não existem | Use `cadastrar_todos.py` para popular o banco |

---

## Observações

1. **Formato de Data**: AAAA-MM-DD (ex: 2026-01-15)
2. **Formato de Horário**: HH:MM:SS (ex: 09:00:00)
3. **IDs**: São gerados automaticamente pelo sistema no cadastro
4. **Pré-requisito**: Os serviços devem estar rodando via `docker-compose up`
5. **Reiniciar banco**: Use `docker-compose down -v` para limpar tudo e recriar
6. **Pagamentos**: Apenas a recepção pode registrar pagamentos

---

## Estrutura do Projeto

```
TrabalhoSD/
├── agendamento/           # Serviço de Agendamento (Python + Socket)
│   ├── interface_agendamento.py  # Gateway REST
│   ├── servico_agendamento.py    # Servidor Socket
│   └── usuario_pb2*.py           # Stubs gRPC gerados
├── adapter/               # Adapter Python para RMI
├── cliente/               # Scripts cliente
│   ├── admin.py, medico.py, paciente.py, recepcionista.py (CLI)
│   ├── cliente_*.py (Interativos)
│   └── cadastrar_todos.py
├── database/              # Scripts SQL
│   └── SD.sql
├── notificacoes/          # Serviço de Notificações (RabbitMQ)
├── usuarios/              # Serviço de Usuários (Java + gRPC)
│   └── servico_java/
├── validacao/             # Serviço de Validação (Java RMI)
├── docker-compose.yaml
└── README.md
```
