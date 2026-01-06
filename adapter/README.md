# Adapter - Ponte Socket/RMI

Este componente implementa uma **ponte (bridge)** entre protocolos Socket TCP e Java RMI, permitindo que serviços Python se comuniquem com o servidor Java RMI de validação de convênios.

## 🎯 Função

Resolve a incompatibilidade de protocolos entre Python e Java RMI:
- **Entrada**: Recebe conexões Socket TCP (porta 7000) com dados em JSON
- **Saída**: Converte para chamadas Java RMI no serviço de validação (porta 1099)

```
┌─────────────────┐     Socket/JSON      ┌─────────────────┐      RMI       ┌─────────────────┐
│  Serviço        │ ──────────────────▶  │     Adapter     │ ────────────▶  │    Validação    │
│  Agendamento    │                      │  (BridgeServer) │                │   (Java RMI)    │
│  (Python)       │ ◀──────────────────  │     :7000       │ ◀────────────  │     :1099       │
└─────────────────┘     JSON Response    └─────────────────┘   boolean      └─────────────────┘
```

## 📁 Estrutura

```
adapter/
├── Dockerfile          # Build e execução do Java
└── src/
    ├── BridgeServer.java   # Servidor Socket que conecta ao RMI
    └── IValidador.java     # Interface RMI (compartilhada com validação)
```

## 🔧 Como Funciona

1. **Inicialização**: O `BridgeServer` aguarda o serviço RMI (`servico_validacao`) estar disponível
2. **Conexão RMI**: Conecta no registry RMI na porta 1099 e obtém o stub `ValidadorService`
3. **Socket Server**: Abre um servidor Socket na porta 7000
4. **Processamento**:
   - Recebe JSON do Python: `{"id_paciente": "123", ...}`
   - Extrai o `id_paciente`
   - Chama `validador.validarConvenio(numeroCartao)` via RMI
   - Retorna JSON: `{"aprovado": true}` ou `{"aprovado": false}`

## 📨 Protocolo de Comunicação

### Request (Python → Adapter)
```json
{"id_paciente": "123", "id_consulta": "456"}
```

### Response (Adapter → Python)
```json
{"aprovado": true}
```

### Regra de Validação
- **ID par**: Convênio aprovado (`true`)
- **ID ímpar**: Convênio rejeitado (`false`)

## 📝 Observação

A implementação atual do sistema usa o `servico-adapter` definido em `validacao/Dockerfile.adapter`, que expõe uma interface HTTP na porta 8084. Este código representa uma abordagem alternativa usando Socket puro.
