# Serviço de Agendamento

Serviço responsável pelo gerenciamento de consultas médicas, incluindo agendamento, cancelamento e pagamentos.

## 🎯 Função

Orquestra o fluxo completo de agendamento de consultas:
1. Verifica existência do paciente via **gRPC** (Serviço de Usuários)
2. Valida convênio via **RMI** (através do Adapter)
3. Persiste dados no **MySQL**
4. Notifica via **RabbitMQ**

```
                                    ┌─────────────────┐
                                    │  Serviço        │
                              gRPC  │  Usuários       │
                           ┌───────▶│    :50051       │
                           │        └─────────────────┘
┌─────────────┐     REST   │   ┌─────────────────┐         ┌─────────────┐
│  Clientes   │ ─────────▶ │   │    Serviço      │────────▶│   MySQL     │
│             │            └───│   Agendamento   │         └─────────────┘
└─────────────┘                │     :5000       │
       ▲        ┌──────────────│   (Socket TCP)  │──────────┐
       │        │              └─────────────────┘          │
       │        ▼                       │                   ▼
┌─────────────────┐                     │           ┌─────────────┐
│    Interface    │                     │ HTTP      │  RabbitMQ   │
│   Agendamento   │◀────── Socket ──────┘           │  (Notif.)   │
│     :8081       │                                 └─────────────┘
└─────────────────┘                      
```

## 📁 Estrutura

```
agendamento/
├── Dockerfile                  # Build Python + gRPC
├── interface_agendamento.py    # Gateway REST (Flask) → Socket
├── servico_agendamento.py      # Servidor Socket principal
├── usuario.proto               # Definição gRPC
└── usuario_pb2*.py             # Stubs gRPC gerados
```

## 🔌 Endpoints REST (Interface)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/agendar` | Agendar nova consulta |
| POST | `/listar_agenda` | Listar agenda do médico |
| POST | `/listar_meus_agendamentos` | Listar consultas do paciente |
| DELETE | `/cancelar_agendamento` | Cancelar consulta |
| POST | `/pagar_consulta` | Registrar pagamento |

## 📨 Ações do Socket

O serviço Socket aceita JSON com campo `acao`:

| Ação | Descrição |
|------|-----------|
| `agendar` | Criar nova consulta |
| `listar_medico` | Buscar consultas por médico |
| `listar_paciente` | Buscar consultas por paciente |
| `cancelar` | Cancelar consulta |
| `pagar` | Registrar pagamento |

## 🐳 Docker

```yaml
servico-agendamento:
  build: ./agendamento
  ports:
    - "5000:5000"
  environment:
    - GRPC_SERVER_HOST=servico-usuarios
    - ADAPTER_HOST=servico-adapter
  depends_on:
    - rabbitmq
    - db
    - servico-usuarios
    - servico-adapter
```

## 🔗 Dependências

- **Python 3.11**
- **MySQL** (banco de dados)
- **RabbitMQ** (notificações)
- **servico-usuarios** (gRPC :50051)
- **servico-adapter** (HTTP → RMI)
