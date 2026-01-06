"""
Script para cadastrar automaticamente todos os tipos de usuários no sistema hospitalar.
Inclui: Usuários, Agendamentos e Pagamentos
Execute com: python cadastrar_todos.py
"""
import requests
from datetime import datetime, timedelta
import random

# Configurações de conexão
API_USUARIOS = "http://localhost:8083"
API_AGENDAMENTO = "http://localhost:8081"

# ============================================
# DADOS DE CADASTRO - 10 DE CADA TIPO
# ============================================

# Administradores (10)
ADMINS = [
    {"nome": "Admin Sistema", "email": "admin@hospital.com", "senha": "admin123", "telefone": "88999990000"},
    {"nome": "Admin Backup", "email": "admin2@hospital.com", "senha": "admin123", "telefone": "88999990001"},
    {"nome": "Admin TI", "email": "admin.ti@hospital.com", "senha": "admin123", "telefone": "88999990002"},
    {"nome": "Admin RH", "email": "admin.rh@hospital.com", "senha": "admin123", "telefone": "88999990003"},
    {"nome": "Admin Financeiro", "email": "admin.fin@hospital.com", "senha": "admin123", "telefone": "88999990004"},
    {"nome": "Admin Operações", "email": "admin.ops@hospital.com", "senha": "admin123", "telefone": "88999990005"},
    {"nome": "Admin Qualidade", "email": "admin.qual@hospital.com", "senha": "admin123", "telefone": "88999990006"},
    {"nome": "Admin Suporte", "email": "admin.sup@hospital.com", "senha": "admin123", "telefone": "88999990007"},
    {"nome": "Admin Segurança", "email": "admin.seg@hospital.com", "senha": "admin123", "telefone": "88999990008"},
    {"nome": "Admin Geral", "email": "admin.geral@hospital.com", "senha": "admin123", "telefone": "88999990009"},
]

# Médicos (10)
MEDICOS = [
    {"nome": "Dr. João Silva", "email": "joao.silva@hospital.com", "senha": "medico123", "telefone": "88999991111", "crm": "12345-CE"},
    {"nome": "Dra. Maria Santos", "email": "maria.santos@hospital.com", "senha": "medico123", "telefone": "88999991112", "crm": "12346-CE"},
    {"nome": "Dr. Carlos Oliveira", "email": "carlos.oliveira@hospital.com", "senha": "medico123", "telefone": "88999991113", "crm": "12347-CE"},
    {"nome": "Dra. Ana Rodrigues", "email": "ana.rodrigues@hospital.com", "senha": "medico123", "telefone": "88999991114", "crm": "12348-CE"},
    {"nome": "Dr. Paulo Mendes", "email": "paulo.mendes@hospital.com", "senha": "medico123", "telefone": "88999991115", "crm": "12349-CE"},
    {"nome": "Dra. Juliana Costa", "email": "juliana.costa@hospital.com", "senha": "medico123", "telefone": "88999991116", "crm": "12350-CE"},
    {"nome": "Dr. Ricardo Almeida", "email": "ricardo.almeida@hospital.com", "senha": "medico123", "telefone": "88999991117", "crm": "12351-CE"},
    {"nome": "Dra. Patricia Lima", "email": "patricia.lima@hospital.com", "senha": "medico123", "telefone": "88999991118", "crm": "12352-CE"},
    {"nome": "Dr. Fernando Souza", "email": "fernando.souza@hospital.com", "senha": "medico123", "telefone": "88999991119", "crm": "12353-CE"},
    {"nome": "Dra. Camila Ferreira", "email": "camila.ferreira@hospital.com", "senha": "medico123", "telefone": "88999991120", "crm": "12354-CE"},
]

# Pacientes (10)
PACIENTES = [
    {"nome": "José Pereira", "email": "jose.pereira@email.com", "senha": "paciente123", "telefone": "88999992221", "problema": "Dor de cabeça frequente"},
    {"nome": "Ana Costa", "email": "ana.costa@email.com", "senha": "paciente123", "telefone": "88999992222", "problema": "Consulta de rotina"},
    {"nome": "Pedro Almeida", "email": "pedro.almeida@email.com", "senha": "paciente123", "telefone": "88999992223", "problema": "Dor nas costas"},
    {"nome": "Lucia Ferreira", "email": "lucia.ferreira@email.com", "senha": "paciente123", "telefone": "88999992224", "problema": "Exames laboratoriais"},
    {"nome": "Marcos Oliveira", "email": "marcos.oliveira@email.com", "senha": "paciente123", "telefone": "88999992225", "problema": "Gripe persistente"},
    {"nome": "Carla Souza", "email": "carla.souza@email.com", "senha": "paciente123", "telefone": "88999992226", "problema": "Dor no joelho"},
    {"nome": "Rafael Santos", "email": "rafael.santos@email.com", "senha": "paciente123", "telefone": "88999992227", "problema": "Alergia respiratória"},
    {"nome": "Fernanda Lima", "email": "fernanda.lima.pac@email.com", "senha": "paciente123", "telefone": "88999992228", "problema": "Pressão alta"},
    {"nome": "Bruno Rodrigues", "email": "bruno.rodrigues@email.com", "senha": "paciente123", "telefone": "88999992229", "problema": "Diabetes controle"},
    {"nome": "Juliana Mendes", "email": "juliana.mendes@email.com", "senha": "paciente123", "telefone": "88999992230", "problema": "Check-up anual"},
]

# Recepcionistas (10)
RECEPCIONISTAS = [
    {"nome": "Fernanda Lima", "email": "fernanda.lima@hospital.com", "senha": "recep123", "telefone": "88999993331"},
    {"nome": "Roberto Souza", "email": "roberto.souza@hospital.com", "senha": "recep123", "telefone": "88999993332"},
    {"nome": "Amanda Silva", "email": "amanda.silva@hospital.com", "senha": "recep123", "telefone": "88999993333"},
    {"nome": "Lucas Oliveira", "email": "lucas.oliveira@hospital.com", "senha": "recep123", "telefone": "88999993334"},
    {"nome": "Mariana Costa", "email": "mariana.costa@hospital.com", "senha": "recep123", "telefone": "88999993335"},
    {"nome": "Diego Santos", "email": "diego.santos@hospital.com", "senha": "recep123", "telefone": "88999993336"},
    {"nome": "Beatriz Almeida", "email": "beatriz.almeida@hospital.com", "senha": "recep123", "telefone": "88999993337"},
    {"nome": "Thiago Ferreira", "email": "thiago.ferreira@hospital.com", "senha": "recep123", "telefone": "88999993338"},
    {"nome": "Larissa Mendes", "email": "larissa.mendes@hospital.com", "senha": "recep123", "telefone": "88999993339"},
    {"nome": "Gabriel Rodrigues", "email": "gabriel.rodrigues@hospital.com", "senha": "recep123", "telefone": "88999993340"},
]

# Agendamentos (serão criados após cadastrar pacientes e médicos)
FORMAS_PAGAMENTO = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX"]
VALORES_CONSULTA = [100.00, 150.00, 200.00, 250.00, 300.00]

# ============================================
# FUNÇÕES DE CADASTRO
# ============================================

def cadastrar_usuario(tipo, dados):
    """Cadastra um usuário genérico"""
    payload = {
        "tipo": tipo,
        "nome": dados["nome"],
        "email": dados["email"],
        "senha": dados["senha"],
        "telefone": dados["telefone"],
    }
    
    if tipo == "medico":
        payload["info_extra"] = dados.get("crm", "")
    elif tipo == "paciente":
        payload["info_extra"] = dados.get("problema", "")
    
    try:
        resp = requests.post(f"{API_USUARIOS}/criar_usuario", json=payload, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if result.get('id') != 0:
                return True, result.get('id')
            else:
                return False, result.get('mensagem', 'Erro desconhecido')
        else:
            return False, resp.text
    except Exception as e:
        return False, str(e)

def criar_agendamento(id_paciente, id_medico, data, horario):
    """Cria um agendamento"""
    payload = {
        "id_paciente": id_paciente,
        "id_medico": id_medico,
        "data": data,
        "horario": horario
    }
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/agendar", json=payload, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            # A API retorna: {"status": "Processado", "resposta_do_servico": "SUCESSO: Consulta X agendada..."}
            resposta = result.get('resposta_do_servico', '')
            if "SUCESSO" in resposta:
                # Extrai o ID da consulta: "SUCESSO: Consulta 123 agendada..."
                import re
                match = re.search(r'Consulta\s+(\d+)', resposta)
                id_consulta = int(match.group(1)) if match else None
                return True, id_consulta
            else:
                return False, resposta
        else:
            return False, resp.text
    except Exception as e:
        return False, str(e)

def pagar_consulta(id_consulta, valor, forma_pagamento):
    """Registra pagamento de uma consulta"""
    payload = {
        "id_consulta": id_consulta,
        "valor": valor,
        "forma_pagamento": forma_pagamento
    }
    try:
        resp = requests.post(f"{API_AGENDAMENTO}/pagar_consulta", json=payload, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if result.get('sucesso'):
                return True, "Pago"
            else:
                return False, result.get('mensagem', 'Erro')
        else:
            return False, resp.text
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("   SCRIPT DE CADASTRO AUTOMÁTICO - SISTEMA HOSPITALAR")
    print("   COM AGENDAMENTOS E PAGAMENTOS")
    print("=" * 70)
    
    resultados = {"sucesso": 0, "falha": 0}
    ids_medicos = []
    ids_pacientes = []
    
    # Cadastrar Administradores
    print("\n📋 Cadastrando ADMINISTRADORES (10)...")
    for admin in ADMINS:
        sucesso, resultado = cadastrar_usuario("admin", admin)
        if sucesso:
            print(f"   ✅ {admin['nome']} - ID: {resultado}")
            resultados["sucesso"] += 1
        else:
            print(f"   ❌ {admin['nome']} - Erro: {resultado}")
            resultados["falha"] += 1
    
    # Cadastrar Médicos
    print("\n👨‍⚕️ Cadastrando MÉDICOS (10)...")
    for medico in MEDICOS:
        sucesso, resultado = cadastrar_usuario("medico", medico)
        if sucesso:
            print(f"   ✅ {medico['nome']} (CRM: {medico['crm']}) - ID: {resultado}")
            ids_medicos.append(resultado)
            resultados["sucesso"] += 1
        else:
            print(f"   ❌ {medico['nome']} - Erro: {resultado}")
            resultados["falha"] += 1
    
    # Cadastrar Pacientes
    print("\n🏥 Cadastrando PACIENTES (10)...")
    for paciente in PACIENTES:
        sucesso, resultado = cadastrar_usuario("paciente", paciente)
        if sucesso:
            print(f"   ✅ {paciente['nome']} - ID: {resultado}")
            ids_pacientes.append(resultado)
            resultados["sucesso"] += 1
        else:
            print(f"   ❌ {paciente['nome']} - Erro: {resultado}")
            resultados["falha"] += 1
    
    # Cadastrar Recepcionistas
    print("\n💼 Cadastrando RECEPCIONISTAS (10)...")
    for recep in RECEPCIONISTAS:
        sucesso, resultado = cadastrar_usuario("recepcionista", recep)
        if sucesso:
            print(f"   ✅ {recep['nome']} - ID: {resultado}")
            resultados["sucesso"] += 1
        else:
            print(f"   ❌ {recep['nome']} - Erro: {resultado}")
            resultados["falha"] += 1
    
    # Criar Agendamentos
    print("\n📅 Criando AGENDAMENTOS (15 consultas)...")
    agendamentos_criados = []
    horarios = ["08:00:00", "09:00:00", "10:00:00", "11:00:00", "14:00:00", "15:00:00", "16:00:00"]
    
    if ids_medicos and ids_pacientes:
        for i in range(15):
            # Datas nos próximos 30 dias
            data_consulta = (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            horario = random.choice(horarios)
            id_paciente = random.choice(ids_pacientes)
            id_medico = random.choice(ids_medicos)
            
            sucesso, resultado = criar_agendamento(id_paciente, id_medico, data_consulta, horario)
            if sucesso:
                print(f"   ✅ Consulta #{i+1} - Paciente {id_paciente} com Médico {id_medico} em {data_consulta} às {horario}")
                if isinstance(resultado, int):
                    agendamentos_criados.append(resultado)
                resultados["sucesso"] += 1
            else:
                print(f"   ❌ Consulta #{i+1} - Erro: {resultado}")
                resultados["falha"] += 1
    else:
        print("   ⚠️ Não foi possível criar agendamentos (faltam médicos ou pacientes)")
    
    # Registrar Pagamentos (para 10 consultas)
    print("\n💰 Registrando PAGAMENTOS (10 consultas)...")
    if agendamentos_criados:
        for i, id_consulta in enumerate(agendamentos_criados[:10]):
            valor = random.choice(VALORES_CONSULTA)
            forma = random.choice(FORMAS_PAGAMENTO)
            
            sucesso, resultado = pagar_consulta(id_consulta, valor, forma)
            if sucesso:
                print(f"   ✅ Pagamento #{i+1} - Consulta {id_consulta}: R$ {valor:.2f} via {forma}")
                resultados["sucesso"] += 1
            else:
                print(f"   ❌ Pagamento #{i+1} - Consulta {id_consulta} - Erro: {resultado}")
                resultados["falha"] += 1
    else:
        print("   ⚠️ Não há consultas para pagar")
    
    # Resumo
    print("\n" + "=" * 70)
    print("                           RESUMO FINAL")
    print("=" * 70)
    print(f"   ✅ Operações com sucesso: {resultados['sucesso']}")
    print(f"   ❌ Operações com falha:   {resultados['falha']}")
    print(f"   📊 Total de operações:   {resultados['sucesso'] + resultados['falha']}")
    print("=" * 70)
    
    # Credenciais de login
    print("\n📝 CREDENCIAIS PARA LOGIN:")
    print("-" * 70)
    print("ADMINISTRADORES (10):")
    for admin in ADMINS[:3]:
        print(f"   Email: {admin['email']} | Senha: {admin['senha']}")
    print(f"   ... e mais {len(ADMINS)-3} administradores")
    
    print("\nMÉDICOS (10):")
    for medico in MEDICOS[:3]:
        print(f"   Email: {medico['email']} | Senha: {medico['senha']}")
    print(f"   ... e mais {len(MEDICOS)-3} médicos")
    
    print("\nPACIENTES (10):")
    for paciente in PACIENTES[:3]:
        print(f"   Email: {paciente['email']} | Senha: {paciente['senha']}")
    print(f"   ... e mais {len(PACIENTES)-3} pacientes")
    
    print("\nRECEPCIONISTAS (10):")
    for recep in RECEPCIONISTAS[:3]:
        print(f"   Email: {recep['email']} | Senha: {recep['senha']}")
    print(f"   ... e mais {len(RECEPCIONISTAS)-3} recepcionistas")
    print("-" * 70)

if __name__ == "__main__":
    main()
