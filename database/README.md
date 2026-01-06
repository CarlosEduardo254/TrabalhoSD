# Database - Banco de Dados

Script SQL de inicialização do banco de dados MySQL para o sistema hospitalar.

## Função

Define a estrutura do banco de dados `hospital_db` com todas as tabelas necessárias para o sistema.

## Estrutura

```
database/
└── SD.sql    # Script de criação das tabelas
```

## Tabelas

| Tabela | Descrição | Chave Primária |
|--------|-----------|----------------|
| `medico` | Dados dos médicos | `id_med` |
| `paciente` | Dados dos pacientes | `id_usuario` |
| `recepcionista` | Dados das recepcionistas | `id_recep` |
| `administradores` | Dados dos administradores | `id_adm` |
| `consulta` | Agendamentos de consultas | `id_consulta` |
| `pagamento` | Registro de pagamentos | `id_pagamento` |

## Relacionamentos

```
paciente ◄───────┐
                 │ FK
medico ◄────┐    │
            │    │
            ▼    ▼
         consulta
            │
            │ FK
            ▼
        pagamento
```

## Docker

O script é executado automaticamente na inicialização do container MySQL:

```yaml
db:
  image: mysql:8.0
  environment:
    MYSQL_ROOT_PASSWORD: 123
    MYSQL_DATABASE: hospital_db
  ports:
    - "3307:3306"
  volumes:
    - ./database/SD.sql:/docker-entrypoint-initdb.d/init.sql
```

## Observação

O banco é **recriado a cada reinício** dos containers. Para limpar completamente:
```powershell
docker-compose down -v
```
