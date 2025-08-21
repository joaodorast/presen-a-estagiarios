#!/usr/bin/env python3
import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append('c:/Users/SEICE/presen-a-estagiarios/seice')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seice.settings')
django.setup()

from core.coleta_simples import buscar_logs_recentes
from core.models import Estagiario, Presenca

print("=== DIAGNÓSTICO: POR QUE REGISTRA ENTRADA E SAÍDA JUNTAS? ===")

# 1. Verificar logs recentes
print("\n1. LOGS RECENTES DO CONTROL ID:")
logs = buscar_logs_recentes()
print(f"Total de logs: {len(logs)}")

if logs:
    print("\nÚltimos 5 logs:")
    for i, log in enumerate(logs[-5:]):
        print(f"  Log {i+1}: user_id={log.get('user_id')}, event={log.get('event')}, time={log.get('time')}")

# 2. Estado atual dos estagiários
print("\n2. ESTADO ATUAL DOS ESTAGIÁRIOS:")
estagiarios = Estagiario.objects.filter(ativo=True)
for est in estagiarios:
    print(f"  {est.nome}: presente={est.presente}, control_id={est.control_id_user_id}")

# 3. Últimas presenças registradas
print("\n3. ÚLTIMAS PRESENÇAS REGISTRADAS:")
presencas = Presenca.objects.all().order_by('-data', '-id')[:5]
for p in presencas:
    print(f"  {p.estagiario.nome} - {p.data}: entrada={p.entrada}, saida={p.saida}, obs={p.observacao}")

# 4. Testar o que acontece quando simula uma passada de rosto
print("\n4. ANÁLISE: O QUE PODE ESTAR CAUSANDO DUPLAS?")

# Verificar se há logs duplicados
if logs:
    user_events = {}
    for log in logs:
        user_id = str(log.get('user_id', ''))
        timestamp = log.get('time')
        event = log.get('event')
        
        if user_id not in user_events:
            user_events[user_id] = []
        user_events[user_id].append({
            'timestamp': timestamp,
            'event': event
        })
    
    print("\nEventos por usuário:")
    for user_id, events in user_events.items():
        try:
            est = Estagiario.objects.get(control_id_user_id=user_id, ativo=True)
            nome = est.nome
        except:
            nome = f"User {user_id}"
        
        print(f"  {nome} ({user_id}):")
        for event in events[-3:]:  # Últimos 3 eventos
            print(f"    Event {event['event']} às {event['timestamp']}")

print("\n=== POSSÍVEIS CAUSAS ===")
print("1. Control ID está gerando múltiplos logs para uma única passada")
print("2. Sistema está processando o mesmo log múltiplas vezes")
print("3. Há delay entre entrada/saída que está causando processamento duplo")
print("4. Estado do estagiário não está sendo atualizado corretamente")
