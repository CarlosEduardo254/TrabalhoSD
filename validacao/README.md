# Serviço de Validação de Convênio

Serviço Java RMI que valida convênios médicos, simulando a comunicação com uma operadora de plano de saúde. Inclui também o **Adapter HTTP** que permite que serviços Python acessem o RMI.

## 🎯 Função

Valida se o convênio do paciente é aceito, permitindo que a consulta seja confirmada automaticamente.

```
┌─────────────────┐     HTTP      ┌─────────────────┐   Subprocess   ┌─────────────────┐
│    Serviço      │ ────────────▶ │  Serviço        │ ────────────▶  │   ClienteRMI    │
│   Agendamento   │               │  Adapter        │                │    (Java)       │
└─────────────────┘               │    :8084        │                └────────┬────────┘
                                  └─────────────────┘                         │ RMI
                                                                              ▼
                                                                    ┌─────────────────┐
                                                                    │   ServidorRMI   │
                                                                    │     :1099       │
                                                                    └─────────────────┘
```

## 📁 Estrutura

```
validacao/
├── Dockerfile              # Build do Servidor RMI (servico-validacao)
├── Dockerfile.adapter      # Build do Adapter HTTP (servico-adapter)
├── interface_validacao.py  # Gateway HTTP (Flask) que chama ClienteRMI
└── src/
    ├── IValidador.java     # Interface RMI
    ├── ServidorRMI.java    # Servidor que expõe o serviço (porta 1099)
    └── ClienteRMI.java     # Cliente que conecta ao servidor RMI
```

## 🔧 Componentes

### 1. Serviço de Validação (servico-validacao)
- **Tecnologia**: Java RMI
- **Porta**: 1099
- **Função**: Expõe o método `validarConvenio()` via RMI Registry

### 2. Serviço Adapter (servico-adapter)
- **Tecnologia**: Python (Flask) + Java (ClienteRMI)
- **Porta**: 8084
- **Função**: Recebe requisições HTTP, executa o `ClienteRMI` via subprocess que conecta ao RMI, e retorna o resultado

O adapter é necessário porque **Python não fala RMI nativamente**. Ele usa Flask para expor uma API HTTP e internamente chama o `ClienteRMI.java` para fazer a comunicação RMI.

## 🔌 Endpoint REST (Adapter)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/validar_convenio` | Validar número do cartão |

### Request
```json
{"numero_cartao": "123456"}
```

### Response
```json
{
  "cartao": "123456",
  "status_convenio": "APROVADO",
  "origem": "Processado via Java RMI"
}
```

## 📋 Regra de Validação

| Último Dígito | Resultado |
|---------------|-----------|
| Par (0, 2, 4, 6, 8) | ✅ APROVADO |
| Ímpar (1, 3, 5, 7, 9) | ❌ REPROVADO |

## 🐳 Docker

```yaml
# Servidor RMI
servico-validacao:
  build: ./validacao
  ports:
    - "1099:1099"

# Adapter HTTP → RMI
servico-adapter:
  build:
    context: ./validacao
    dockerfile: Dockerfile.adapter
  ports:
    - "8084:8084"
  environment:
    - RMI_HOST=servico-validacao
  depends_on:
    - servico-validacao
```

## 🔗 Dependências

- **Java 21** (Eclipse Temurin)
- **Python 3.9** (Flask)
