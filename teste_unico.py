#!/usr/bin/env python3
import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append('c:/Users/SEICE/presen-a-estagiarios/seice')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seice.settings')
django.setup()

from core.coleta_simples import *
from core.models import Estagiario, Presenca
import logging
logging.basicConfig(level=logging.INFO)

print("=== TESTE: PROCESSAMENTO ÚNICO DE LOGS ===")

# 1. Resetar sistema
print("\n1. RESETANDO SISTEMA...")
resetar_controle_logs()

# 2. Verificar estado inicial
print("\n2. ESTADO INICIAL DOS ESTAGIÁRIOS:")
estagiarios = Estagiario.objects.filter(ativo=True)
for est in estagiarios:
    print(f"  {est.nome}: presente={est.presente}, control_id={est.control_id_user_id}")

# 3. Testar uma coleta
print("\n3. TESTANDO COLETA ÚNICA...")
try:
    registrar_presencas_dos_logs()
except Exception as e:
    print(f"Erro na coleta: {e}")

# 4. Verificar estado após processamento
print("\n4. ESTADO APÓS PRIMEIRA COLETA:")
for est in estagiarios:
    est.refresh_from_db()
    print(f"  {est.nome}: presente={est.presente}")

# 5. Testar segunda coleta (deve detectar duplicatas)
print("\n5. TESTANDO SEGUNDA COLETA (deve evitar duplicatas)...")
try:
    registrar_presencas_dos_logs()
except Exception as e:
    print(f"Erro na segunda coleta: {e}")

# 6. Status do cache
print("\n6. STATUS DO CACHE:")
status = status_coleta()
print(f"  Cache de logs processados: {status['cache_logs']['total_logs_cache']} itens")
print(f"  Total processados: {status['ultimo_processamento']['total_processados']}")

# 7. Verificar últimas presenças
print("\n7. ÚLTIMAS PRESENÇAS REGISTRADAS:")
presencas = Presenca.objects.all().order_by('-data', '-id')[:3]
for p in presencas:
    print(f"  {p.estagiario.nome} - {p.data}: entrada={p.entrada}, saida={p.saida}")

print("\n=== TESTE CONCLUÍDO ===")
print("Se tudo funcionou corretamente:")
print("1. Primeira coleta processou logs novos")
print("2. Segunda coleta não processou duplicatas")
print("3. Cache mantém controle dos logs processados")
