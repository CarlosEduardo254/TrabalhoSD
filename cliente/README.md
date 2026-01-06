# Planilha de Mapeamento - Scripts Cliente

## Sistema de Gerenciamento de Consultas Médicas - Sistemas Distribuídos 2025.2

---

## 🚀 INICIALIZAÇÃO DO SISTEMA

| AÇÃO | COMANDO | DESCRIÇÃO |
|------|---------|-----------|
| Levantar todos os serviços | `docker-compose up --build` | Inicia todos os containers (MySQL, RabbitMQ, serviços) |
| Levantar em background | `docker-compose up --build -d` | Inicia em modo detached (libera o terminal) |
| Parar todos os serviços | `docker-compose down` | Para e remove os containers |
| Parar e limpar volumes | `docker-compose down -v` | Para containers e **APAGA O BANCO DE DADOS** |
| Ver logs | `docker-compose logs -f` | Mostra logs em tempo real |
| Ver status | `docker-compose ps` | Lista containers em execução |

### ⚠️ Importante
- Execute os comandos Docker na **raiz do projeto** (onde está o `docker-compose.yaml`)
- Aguarde todos os serviços ficarem "healthy" antes de executar os scripts cliente
- O banco de dados é recriado automaticamente ao subir os serviços

---

## 📋 PACIENTE (paciente.py)

| AÇÃO | SCRIPT | COMO EXECUTAR? |
|------|--------|----------------|
| Criar paciente | paciente.py | `cd cliente`<br>`python paciente.py criar "José Silva" "jose@email.com" "senha123" "88999991111" "Dor de cabeça"` |
| Login | paciente.py | `python paciente.py login "jose@email.com" "senha123"` |
| Agendar consulta (convênio) | paciente.py | `python paciente.py agendar 1 1 "2026-01-15" "09:00:00"` |
| Agendar consulta (particular) | paciente.py | `python paciente.py agendar 1 1 "2026-01-15" "10:00:00" particular`<br>OU<br>`python paciente.py particular 1 1 "2026-01-15" "10:00:00"` |
| Listar consultas | paciente.py | `python paciente.py listar 1` |
| Cancelar consulta | paciente.py | `python paciente.py cancelar 1 5` |
| Atualizar dados | paciente.py | `python paciente.py atualizar 1 "José Silva" "jose@email.com" "novasenha" "88999991111" "Dor de cabeça"` |
| Deletar conta | paciente.py | `python paciente.py deletar 1` |

> **Nota:** Pagamentos são realizados apenas pela RECEPÇÃO (recepcionista.py)

---

## 👨‍⚕️ MÉDICO (medico.py)

| AÇÃO | SCRIPT | COMO EXECUTAR? |
|------|--------|----------------|
| Criar médico | medico.py | `cd cliente`<br>`python medico.py criar "Dr. João Silva" "joao@hospital.com" "senha123" "88999991111" "12345-CE"` |
| Login | medico.py | `python medico.py login "joao@hospital.com" "senha123"` |
| Ver agenda | medico.py | `python medico.py agenda 1` |
| Atualizar dados | medico.py | `python medico.py atualizar 1 "Dr. João Silva" "joao@hospital.com" "novasenha" "88999991112" "12345-CE"` |
| Deletar conta | medico.py | `python medico.py deletar 1` |

---

## 🔧 ADMINISTRADOR (admin.py)

| AÇÃO | SCRIPT | COMO EXECUTAR? |
|------|--------|----------------|
| Criar admin | admin.py | `cd cliente`<br>`python admin.py criar "Admin Sistema" "admin@hospital.com" "admin123" "88999990000"` |
| Login | admin.py | `python admin.py login "admin@hospital.com" "admin123"` |
| Listar pacientes | admin.py | `python admin.py listar_pacientes` |
| Listar médicos | admin.py | `python admin.py listar_medicos` |
| Listar recepcionistas | admin.py | `python admin.py listar_recepcionistas` |
| Listar admins | admin.py | `python admin.py listar_admins` |
| Listar todos | admin.py | `python admin.py listar_todos` |
| Atualizar dados | admin.py | `python admin.py atualizar 1 "Admin Sistema" "admin@hospital.com" "novasenha" "88999990001"` |
| Deletar conta | admin.py | `python admin.py deletar 1` |

---

## 💼 RECEPCIONISTA (recepcionista.py)

| AÇÃO | SCRIPT | COMO EXECUTAR? |
|------|--------|----------------|
| Criar recepcionista | recepcionista.py | `cd cliente`<br>`python recepcionista.py criar "Fernanda Lima" "fernanda@hospital.com" "recep123" "88999993331"` |
| Login | recepcionista.py | `python recepcionista.py login "fernanda@hospital.com" "recep123"` |
| Ver agenda de médico | recepcionista.py | `python recepcionista.py agenda 1` |
| Agendar para paciente (convênio) | recepcionista.py | `python recepcionista.py agendar 1 1 "2026-01-15" "10:00:00"` |
| Agendar para paciente (particular) | recepcionista.py | `python recepcionista.py agendar 1 1 "2026-01-15" "11:00:00" particular`<br>OU<br>`python recepcionista.py particular 1 1 "2026-01-15" "11:00:00"` |
| Cancelar consulta | recepcionista.py | `python recepcionista.py cancelar 5` |
| **Registrar pagamento** | recepcionista.py | `python recepcionista.py pagar 1 200.00 "Cartão de Crédito"` |
| Atualizar dados | recepcionista.py | `python recepcionista.py atualizar 1 "Fernanda Lima" "fernanda@hospital.com" "novasenha" "88999993332"` |
| Deletar conta | recepcionista.py | `python recepcionista.py deletar 1` |

> **Nota:** Apenas a RECEPÇÃO pode registrar pagamentos de consultas!

---

## 📝 Script de Cadastro Automático

| AÇÃO | SCRIPT | COMO EXECUTAR? |
|------|--------|----------------|
| Cadastrar todos os usuários de teste | cadastrar_todos.py | `cd cliente`<br>`python cadastrar_todos.py` |

Este script cadastra automaticamente:
- 10 Administradores
- 10 Médicos
- 10 Pacientes
- 10 Recepcionistas
- 15 Agendamentos
- 10 Pagamentos

---

## 🏥 Tipos de Consulta

| Tipo | Descrição | Status Inicial |
|------|-----------|----------------|
| **Convênio** | Validação automática pelo sistema | CONFIRMADA (se ID par) ou PENDENTE (se ID ímpar) |
| **Particular** | Sem convênio, requer pagamento | Sempre PENDENTE até pagar |

---

## 🔗 Formas de Pagamento Aceitas

- `Dinheiro`
- `PIX`
- `Cartão de Crédito`
- `Cartão de Débito`

---

## 📌 Observações

1. **Formato de Data**: AAAA-MM-DD (ex: 2026-01-15)
2. **Formato de Horário**: HH:MM:SS (ex: 09:00:00)
3. **IDs**: São gerados automaticamente pelo sistema no cadastro
4. **Pré-requisito**: Os serviços devem estar rodando via `docker-compose up`
5. **Consultas Particulares**: Usar o 5º argumento "particular" ou o comando "particular"
6. **Reiniciar banco**: Use `docker-compose down -v` para limpar tudo e recriar
7. **Pagamentos**: Apenas a recepção pode registrar pagamentos
