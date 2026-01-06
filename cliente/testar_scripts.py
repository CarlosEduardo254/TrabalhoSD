"""
Script de TESTE GERAL para validar todos os scripts CLI.
Executa operações de cada tipo de usuário e valida respostas.

Uso: python testar_scripts.py

Requisitos:
  - Ter executado cadastrar_todos.py antes
  - Serviços rodando (porta 8083 e 8081)
"""
import subprocess
import sys
import os

# Cores para output (desabilitadas para Windows)
class Cores:
    OK = ''       # Verde
    ERRO = ''     # Vermelho
    WARN = ''     # Amarelo
    INFO = ''     # Azul
    RESET = ''    # Reset

def executar(comando):
    """Executa um comando e retorna (sucesso, output)"""
    try:
        result = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            encoding='utf-8',
            errors='replace'
        )
        output = result.stdout + result.stderr
        sucesso = "SUCESSO" in output or "INFO" in output or result.returncode == 0
        return sucesso, output.strip()
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: Comando demorou mais de 15 segundos"
    except Exception as e:
        return False, f"EXCEPTION: {str(e)}"

def testar(descricao, comando, espera_sucesso=True):
    """Executa um teste e reporta resultado"""
    sucesso, output = executar(comando)
    
    # Verifica se o output indica erro
    tem_erro = "ERRO:" in output and "ERRO: Este usuário não é" not in output
    
    if espera_sucesso:
        passou = sucesso and not tem_erro
    else:
        passou = not sucesso or tem_erro
    
    status = f"{Cores.OK}✅ PASSOU{Cores.RESET}" if passou else f"{Cores.ERRO}❌ FALHOU{Cores.RESET}"
    print(f"  {status} | {descricao}")
    
    # Mostra detalhes se falhou
    if not passou:
        for linha in output.split('\n')[:5]:
            print(f"      {Cores.WARN}{linha}{Cores.RESET}")
    
    return passou

def rodar_testes():
    print("=" * 70)
    print("            TESTE GERAL DOS SCRIPTS CLI")
    print("=" * 70)
    
    resultados = {"passou": 0, "falhou": 0}
    
    # =====================================================
    # TESTES DO ADMIN
    # =====================================================
    print(f"\n{Cores.INFO}📋 TESTANDO: admin.py{Cores.RESET}")
    print("-" * 50)
    
    testes_admin = [
        ("Login admin válido", 'python admin.py login "admin@hospital.com" "admin123"'),
        ("Login admin senha errada", 'python admin.py login "admin@hospital.com" "senhaerrada"', False),
        ("Listar pacientes", 'python admin.py listar_pacientes'),
        ("Listar médicos", 'python admin.py listar_medicos'),
        ("Listar recepcionistas", 'python admin.py listar_recepcionistas'),
        ("Listar admins", 'python admin.py listar_admins'),
        ("Listar todos", 'python admin.py listar_todos'),
        ("Ajuda", 'python admin.py ajuda'),
    ]
    
    for teste in testes_admin:
        espera = teste[2] if len(teste) > 2 else True
        if testar(teste[0], teste[1], espera):
            resultados["passou"] += 1
        else:
            resultados["falhou"] += 1

    # =====================================================
    # TESTES DO MÉDICO
    # =====================================================
    print(f"\n{Cores.INFO}👨‍⚕️ TESTANDO: medico.py{Cores.RESET}")
    print("-" * 50)
    
    testes_medico = [
        ("Login médico válido", 'python medico.py login "joao.silva@hospital.com" "medico123"'),
        ("Login médico senha errada", 'python medico.py login "joao.silva@hospital.com" "errada"', False),
        ("Ver agenda médico ID 1", 'python medico.py agenda 1'),
        ("Ver agenda médico ID 2", 'python medico.py agenda 2'),
        ("Ajuda", 'python medico.py ajuda'),
    ]
    
    for teste in testes_medico:
        espera = teste[2] if len(teste) > 2 else True
        if testar(teste[0], teste[1], espera):
            resultados["passou"] += 1
        else:
            resultados["falhou"] += 1

    # =====================================================
    # TESTES DO PACIENTE
    # =====================================================
    print(f"\n{Cores.INFO}🏥 TESTANDO: paciente.py{Cores.RESET}")
    print("-" * 50)
    
    testes_paciente = [
        ("Login paciente válido", 'python paciente.py login "jose.pereira@email.com" "paciente123"'),
        ("Login paciente senha errada", 'python paciente.py login "jose.pereira@email.com" "errada"', False),
        ("Listar consultas paciente ID 1", 'python paciente.py listar 1'),
        ("Listar consultas paciente ID 2", 'python paciente.py listar 2'),
        ("Agendar consulta (convênio)", 'python paciente.py agendar 1 1 2026-02-15 10:00:00'),
        ("Agendar consulta (particular)", 'python paciente.py particular 2 2 2026-02-16 11:00:00'),
        ("Ajuda", 'python paciente.py ajuda'),
    ]
    
    for teste in testes_paciente:
        espera = teste[2] if len(teste) > 2 else True
        if testar(teste[0], teste[1], espera):
            resultados["passou"] += 1
        else:
            resultados["falhou"] += 1

    # =====================================================
    # TESTES DO RECEPCIONISTA
    # =====================================================
    print(f"\n{Cores.INFO}💼 TESTANDO: recepcionista.py{Cores.RESET}")
    print("-" * 50)
    
    testes_recepcionista = [
        ("Login recepcionista válido", 'python recepcionista.py login "fernanda.lima@hospital.com" "recep123"'),
        ("Login recepcionista senha errada", 'python recepcionista.py login "fernanda.lima@hospital.com" "errada"', False),
        ("Ver agenda médico ID 1", 'python recepcionista.py agenda 1'),
        ("Agendar para paciente (convênio)", 'python recepcionista.py agendar 3 3 2026-02-17 14:00:00'),
        ("Agendar para paciente (particular)", 'python recepcionista.py particular 4 4 2026-02-18 15:00:00'),
        ("Ajuda", 'python recepcionista.py ajuda'),
    ]
    
    for teste in testes_recepcionista:
        espera = teste[2] if len(teste) > 2 else True
        if testar(teste[0], teste[1], espera):
            resultados["passou"] += 1
        else:
            resultados["falhou"] += 1

    # =====================================================
    # TESTES DE FLUXO COMPLETO
    # =====================================================
    print(f"\n{Cores.INFO}🔄 TESTANDO: FLUXO COMPLETO (Agendar -> Pagar -> Cancelar){Cores.RESET}")
    print("-" * 50)
    
    # 1. Cria um novo paciente para teste
    teste_email = "teste.fluxo@teste.com"
    if testar("Criar paciente de teste", f'python paciente.py criar "Paciente Teste" "{teste_email}" "teste123" "88999990000" "Teste de fluxo"'):
        resultados["passou"] += 1
    else:
        resultados["falhou"] += 1
    
    # 2. Login do paciente
    if testar("Login paciente teste", f'python paciente.py login "{teste_email}" "teste123"'):
        resultados["passou"] += 1
    else:
        resultados["falhou"] += 1

    # =====================================================
    # RESUMO
    # =====================================================
    print("\n" + "=" * 70)
    print("                         RESUMO DOS TESTES")
    print("=" * 70)
    total = resultados["passou"] + resultados["falhou"]
    pct = (resultados["passou"] / total * 100) if total > 0 else 0
    
    print(f"  {Cores.OK}✅ Passou: {resultados['passou']}{Cores.RESET}")
    print(f"  {Cores.ERRO}❌ Falhou: {resultados['falhou']}{Cores.RESET}")
    print(f"  📊 Total:  {total}")
    print(f"  📈 Taxa:   {pct:.1f}%")
    print("=" * 70)
    
    if resultados["falhou"] > 0:
        print(f"\n{Cores.WARN}⚠️  Alguns testes falharam. Verifique os erros acima.{Cores.RESET}")
        return 1
    else:
        print(f"\n{Cores.OK}🎉 Todos os testes passaram!{Cores.RESET}")
        return 0

if __name__ == "__main__":
    sys.exit(rodar_testes())
