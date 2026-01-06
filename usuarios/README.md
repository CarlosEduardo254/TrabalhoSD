# Serviço de Usuários

Serviço responsável pelo gerenciamento de todos os tipos de usuários do sistema (pacientes, médicos, recepcionistas e administradores).

## Função

Gerencia o CRUD completo de usuários e autenticação via gRPC.

```
┌─────────────────┐     REST      ┌─────────────────┐     gRPC      ┌─────────────────┐
│    Clientes     │ ────────────▶ │    Interface    │ ────────────▶ │    Serviço      │
│                 │               │    Usuários     │               │    Usuários     │
│                 │ ◀──────────── │     :8083       │ ◀──────────── │   (Java/Spring) │
└─────────────────┘               └─────────────────┘               │     :50051      │
                                                                    └────────┬────────┘
                                                                             │
                                                                             ▼
                                                                    ┌─────────────────┐
                                                                    │     MySQL       │
                                                                    └─────────────────┘
```

## Estrutura

```
usuarios/
├── interface_usuarios.py   # Gateway REST (Flask) → gRPC
├── usuario.proto           # Definição do serviço gRPC
├── usuario_pb2*.py         # Stubs Python gerados
└── servico_java/           # Servidor gRPC (Java Spring Boot)
    ├── pom.xml
    ├── Dockerfile
    └── src/main/java/...
```

## Endpoints REST (Interface)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/criar_usuario` | Criar novo usuário |
| POST | `/login` | Autenticação |
| PUT | `/atualizar_usuario` | Atualizar dados |
| DELETE | `/deletar_usuario` | Excluir usuário |
| POST | `/listar_usuarios` | Listar por tipo |

## Métodos gRPC

| Método | Descrição |
|--------|-----------|
| `CriarUsuario` | Criar usuário de qualquer tipo |
| `Login` | Autenticação por email/senha |
| `VerificarUsuario` | Verificar se usuário existe |
| `AtualizarUsuario` | Atualizar dados do usuário |
| `DeletarUsuario` | Excluir usuário |
| `ListarUsuarios` | Listar usuários por tipo |

## Tipos de Usuário

| Tipo | Campo Extra |
|------|-------------|
| `paciente` | problema (descrição do problema de saúde) |
| `medico` | CRM |
| `recepcionista` | - |
| `admin` | - |

## Docker

```yaml
servico-usuarios:
  build: ./usuarios/servico_java
  ports:
    - "50051:50051"
  depends_on:
    db:
      condition: service_healthy

interface-usuarios:
  build: .
  command: python usuarios/interface_usuarios.py
  ports:
    - "8083:8083"
  depends_on:
    - servico-usuarios
```

## Dependências

- **Java 21** (Spring Boot)
- **Python 3.11** (Flask + gRPC)
- **MySQL** (banco de dados)
