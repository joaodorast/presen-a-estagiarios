#!/usr/bin/env python3
"""
TESTE SISTEMA v2.0 - Processa apenas LOGS NOVOS
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def testar_sistema_v2():
    print("🚀 TESTE SISTEMA v2.0 - LOGS NOVOS")
    print("=" * 50)
    
    print("📋 RECURSOS v2.0:")
    print("   🔍 Detecta apenas logs NOVOS")
    print("   📥 Identifica ENTRADA corretamente")
    print("   📤 Identifica SAÍDA corretamente") 
    print("   ⏱️ Calcula horas trabalhadas")
    print("   🚫 Evita reprocessar logs antigos")
    
    # 1. Status inicial
    print("\n1️⃣ Status inicial...")
    verificar_status()
    
    # 2. Reset para teste
    print("\n2️⃣ Resetando controle para teste...")
    resetar_controle()
    
    # 3. Primeira coleta (vai processar tudo como novo)
    print("\n3️⃣ Primeira coleta (tudo será novo)...")
    coleta_manual()
    
    # 4. Segunda coleta (não deve processar nada)
    print("\n4️⃣ Segunda coleta (nada deve ser novo)...")
    coleta_manual()
    
    # 5. Status final
    print("\n5️⃣ Status final...")
    verificar_status()
    
    print("\n✅ Teste concluído!")
    print("\n🎯 RESULTADO ESPERADO:")
    print("   ✅ Primeira coleta: processou logs")
    print("   ✅ Segunda coleta: nenhum log novo")
    print("   ✅ Sistema evita reprocessamento!")

def verificar_status():
    try:
        response = requests.get(f"{BASE_URL}/api/presencas-auto/status/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sistema: {data['sistema']}")
            status = data['status']
            print(f"🔄 Ativo: {status['ativa']}")
            
            ultimo = status.get('ultimo_processamento', {})
            print(f"📊 Total processado: {ultimo.get('total_processados', 0)}")
            print(f"🕐 Último: {ultimo.get('timestamp', 'Nunca')}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def resetar_controle():
    try:
        response = requests.post(
            f"{BASE_URL}/api/presencas-auto/controle/",
            json={"action": "reset"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def coleta_manual():
    try:
        response = requests.post(f"{BASE_URL}/api/presencas-auto/manual/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_sistema_v2()
