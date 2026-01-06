# Planilha de Mapeamento - Scripts Cliente

## Sistema de Gerenciamento de Consultas Médicas - Sistemas Distribuídos 2025.2

---

## IMAGEM DOCKER DO CLIENTE

**Docker Hub:** [carloseduardo42/cliente-hospital](https://hub.docker.com/r/carloseduardo42/cliente-hospital)

```bash
# Baixar a imagem
docker pull carloseduardo42/cliente-hospital:latest
```

---

## INICIALIZAÇÃO DO SISTEMA

| AÇÃO | COMANDO | DESCRIÇÃO |
|------|---------|-----------|
| Levantar todos os serviços | `docker-compose up --build` | Inicia todos os containers (MySQL, RabbitMQ, serviços) |
| Levantar em background | `docker-compose up --build -d` | Inicia em modo detached (libera o terminal) |
| Parar todos os serviços | `docker-compose down` | Para e remove os containers |
| Parar e limpar volumes | `docker-compose down -v` | Para containers e **APAGA O BANCO DE DADOS** |
| Ver logs | `docker-compose logs -f` | Mostra logs em tempo real |
| Ver status | `docker-compose ps` | Lista containers em execução |

### Importante
- Execute os comandos Docker na **raiz do projeto** (onde está o `docker-compose.yaml`)
- Aguarde todos os serviços ficarem "healthy" antes de executar os scripts cliente
- O banco de dados é recriado automaticamente ao subir os serviços

---

## COMO EXECUTAR OS SCRIPTS

### Opção 1: Execução Local (Python instalado)
```bash
cd cliente
python <script>.py <comando> <argumentos>
```

### Opção 2: Execução via Docker (baixando do Docker Hub)
```bash
docker run -it --rm --network host carloseduardo42/cliente-hospital python <script>.py <comando> <argumentos>
```

> **Nota:** O `--network host` permite que o container acesse os serviços rodando no host.

---

## PACIENTE (paciente.py)

| AÇÃO | EXECUÇÃO LOCAL | EXECUÇÃO VIA DOCKER |
|------|----------------|---------------------|
| Criar paciente | `python paciente.py criar "José Silva" "jose@email.com" "senha123" "88999991111" "Dor de cabeça"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python paciente.py criar "José Silva" "jose@email.com" "senha123" "88999991111" "Dor de cabeça"` |
| Login | `python paciente.py login "jose@email.com" "senha123"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python paciente.py login "jose@email.com" "senha123"` |
| Agendar consulta (convênio) | `python paciente.py agendar 1 1 "2026-01-15" "09:00:00"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python paciente.py agendar 1 1 "2026-01-15" "09:00:00"` |
| Agendar consulta (particular) | `python paciente.py particular 1 1 "2026-01-15" "10:00:00"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python paciente.py particular 1 1 "2026-01-15" "10:00:00"` |
| Listar consultas | `python paciente.py listar 1` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python paciente.py listar 1` |
| Cancelar consulta | `python paciente.py cancelar 1 5` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python paciente.py cancelar 1 5` |
| Atualizar dados | `python paciente.py atualizar 1 "José" "jose@email.com" "novasenha" "88999991111" "Dor"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python paciente.py atualizar 1 "José" "jose@email.com" "novasenha" "88999991111" "Dor"` |
| Deletar conta | `python paciente.py deletar 1` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python paciente.py deletar 1` |

> **Nota:** Pagamentos são realizados apenas pela RECEPÇÃO (recepcionista.py)

---

## MÉDICO (medico.py)

| AÇÃO | EXECUÇÃO LOCAL | EXECUÇÃO VIA DOCKER |
|------|----------------|---------------------|
| Criar médico | `python medico.py criar "Dr. João" "joao@hospital.com" "senha123" "88999991111" "12345-CE"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python medico.py criar "Dr. João" "joao@hospital.com" "senha123" "88999991111" "12345-CE"` |
| Login | `python medico.py login "joao@hospital.com" "senha123"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python medico.py login "joao@hospital.com" "senha123"` |
| Ver agenda | `python medico.py agenda 1` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python medico.py agenda 1` |
| Atualizar dados | `python medico.py atualizar 1 "Dr. João" "joao@hospital.com" "novasenha" "88999991112" "12345-CE"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python medico.py atualizar 1 "Dr. João" "joao@hospital.com" "novasenha" "88999991112" "12345-CE"` |
| Deletar conta | `python medico.py deletar 1` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python medico.py deletar 1` |

---

## ADMINISTRADOR (admin.py)

| AÇÃO | EXECUÇÃO LOCAL | EXECUÇÃO VIA DOCKER |
|------|----------------|---------------------|
| Criar admin | `python admin.py criar "Admin" "admin@hospital.com" "admin123" "88999990000"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python admin.py criar "Admin" "admin@hospital.com" "admin123" "88999990000"` |
| Login | `python admin.py login "admin@hospital.com" "admin123"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python admin.py login "admin@hospital.com" "admin123"` |
| Listar pacientes | `python admin.py listar_pacientes` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python admin.py listar_pacientes` |
| Listar médicos | `python admin.py listar_medicos` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python admin.py listar_medicos` |
| Listar recepcionistas | `python admin.py listar_recepcionistas` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python admin.py listar_recepcionistas` |
| Listar admins | `python admin.py listar_admins` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python admin.py listar_admins` |
| Listar todos | `python admin.py listar_todos` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python admin.py listar_todos` |
| Atualizar dados | `python admin.py atualizar 1 "Admin" "admin@hospital.com" "novasenha" "88999990001"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python admin.py atualizar 1 "Admin" "admin@hospital.com" "novasenha" "88999990001"` |
| Deletar conta | `python admin.py deletar 1` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python admin.py deletar 1` |

---

## RECEPCIONISTA (recepcionista.py)

| AÇÃO | EXECUÇÃO LOCAL | EXECUÇÃO VIA DOCKER |
|------|----------------|---------------------|
| Criar recepcionista | `python recepcionista.py criar "Fernanda" "fernanda@hospital.com" "recep123" "88999993331"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python recepcionista.py criar "Fernanda" "fernanda@hospital.com" "recep123" "88999993331"` |
| Login | `python recepcionista.py login "fernanda@hospital.com" "recep123"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python recepcionista.py login "fernanda@hospital.com" "recep123"` |
| Ver agenda de médico | `python recepcionista.py agenda 1` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python recepcionista.py agenda 1` |
| Agendar (convênio) | `python recepcionista.py agendar 1 1 "2026-01-15" "10:00:00"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python recepcionista.py agendar 1 1 "2026-01-15" "10:00:00"` |
| Agendar (particular) | `python recepcionista.py particular 1 1 "2026-01-15" "11:00:00"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python recepcionista.py particular 1 1 "2026-01-15" "11:00:00"` |
| Cancelar consulta | `python recepcionista.py cancelar 5` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python recepcionista.py cancelar 5` |
| **Registrar pagamento** | `python recepcionista.py pagar 1 200.00 "Cartão de Crédito"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python recepcionista.py pagar 1 200.00 "Cartão de Crédito"` |
| Atualizar dados | `python recepcionista.py atualizar 1 "Fernanda" "fernanda@hospital.com" "novasenha" "88999993332"` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python recepcionista.py atualizar 1 "Fernanda" "fernanda@hospital.com" "novasenha" "88999993332"` |
| Deletar conta | `python recepcionista.py deletar 1` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python recepcionista.py deletar 1` |

> **Nota:** Apenas a RECEPÇÃO pode registrar pagamentos de consultas!

---

## Script de Cadastro Automático

| AÇÃO | EXECUÇÃO LOCAL | EXECUÇÃO VIA DOCKER |
|------|----------------|---------------------|
| Cadastrar todos os usuários de teste | `python cadastrar_todos.py` | `docker run -it --rm --network host carloseduardo42/cliente-hospital python cadastrar_todos.py` |

Este script cadastra automaticamente:
- 10 Administradores
- 10 Médicos
- 10 Pacientes
- 10 Recepcionistas
- 15 Agendamentos
- 10 Pagamentos

---

## Tipos de Consulta

| Tipo | Descrição | Status Inicial |
|------|-----------|----------------|
| **Convênio** | Validação automática pelo sistema | CONFIRMADA (se ID par) ou PENDENTE (se ID ímpar) |
| **Particular** | Sem convênio, requer pagamento | Sempre PENDENTE até pagar |

---

## Formas de Pagamento Aceitas

- `Dinheiro`
- `PIX`
- `Cartão de Crédito`
- `Cartão de Débito`

---

## Observações

1. **Formato de Data**: AAAA-MM-DD (ex: 2026-01-15)
2. **Formato de Horário**: HH:MM:SS (ex: 09:00:00)
3. **IDs**: São gerados automaticamente pelo sistema no cadastro
4. **Pré-requisito**: Os serviços devem estar rodando via `docker-compose up`
5. **Consultas Particulares**: Usar o comando "particular"
6. **Reiniciar banco**: Use `docker-compose down -v` para limpar tudo e recriar
7. **Pagamentos**: Apenas a recepção pode registrar pagamentos
