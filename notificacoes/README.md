# Serviço de Notificações

Worker que processa mensagens assíncronas de notificação via RabbitMQ, simulando o envio de emails de confirmação.

## Função

Consome mensagens da fila `email_queue` e simula o envio de emails para confirmação de agendamentos.

```
┌─────────────────┐      Publica      ┌─────────────────┐     Consome      ┌─────────────────┐
│    Serviço      │ ────────────────▶ │    RabbitMQ     │ ───────────────▶ │     Worker      │
│   Agendamento   │                   │   email_queue   │                  │   Notificações  │
└─────────────────┘                   └─────────────────┘                  └─────────────────┘
                                                                                   │
                                                                                   ▼
                                                                              Simula Email
```

## Estrutura

```
notificacoes/
├── Dockerfile          # Build Python + pika
└── worker_email.py     # Consumer RabbitMQ
```

## Como Funciona

1. **Conexão**: Conecta ao RabbitMQ (com retry automático)
2. **Fila**: Declara/conecta na fila `email_queue`
3. **Consume**: Escuta mensagens de forma contínua
4. **Processa**: Simula envio de email para cada mensagem recebida

## Formato da Mensagem

O worker recebe strings de texto simples:
```
Agendamento confirmado para Médico 1 na data 2026-01-15 às 09:00:00
```

## Docker

```yaml
servico-notificacoes:
  build: ./notificacoes
  depends_on:
    rabbitmq:
      condition: service_healthy
```

## Dependências

- **Python 3.9**
- **RabbitMQ** (mensageria)
- **pika** (cliente AMQP)
