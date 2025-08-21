#!/usr/bin/env python3
"""
TESTE SUPER SIMPLES - Sistema de Presenças Automáticas
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def testar_sistema_simples():
    print("🎯 TESTE SUPER SIMPLES - PRESENÇAS AUTOMÁTICAS")
    print("=" * 50)
    
    # 1. Verificar status
    print("1️⃣ Verificando status...")
    try:
        response = requests.get(f"{BASE_URL}/api/presencas-auto/status/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sistema: {data['sistema']}")
            print(f"🔄 Ativo: {data['status']['ativa']}")
            print(f"🧵 Thread: {data['status']['thread_viva']}")
            print(f"⏱️ Intervalo: {data['status']['intervalo']}s")
            print(f"🌐 Control ID: {data['status']['control_id_ip']}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 2. Teste manual
    print("\n2️⃣ Executando coleta manual...")
    try:
        response = requests.post(f"{BASE_URL}/api/presencas-auto/manual/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n✅ Teste concluído!")
    print("\n📝 O que o sistema faz:")
    print("   🔄 Coleta logs do Control ID a cada 30s")
    print("   📝 Registra presenças automaticamente")
    print("   ⚡ Funciona sozinho enquanto servidor estiver ligado")
    print("\n🎉 É isso! Super simples!")

if __name__ == "__main__":
    testar_sistema_simples()
