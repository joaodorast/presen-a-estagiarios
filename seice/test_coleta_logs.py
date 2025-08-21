#!/usr/bin/env python3
"""
Script de teste para a coleta de logs do Control ID
"""

import requests
import json
import time

# Configurações
BASE_URL = "http://127.0.0.1:8000"
CONTROL_ID_IP = "192.168.3.40:81"

def testar_coleta_manual():
    """Testa a coleta manual de logs"""
    print("\n=== TESTE: COLETA MANUAL DE LOGS ===")

    url = f"{BASE_URL}/dashboard/api/control-id/logs/manual/"
    data = {
        "control_id_ip": CONTROL_ID_IP
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso: {result['message']}")
            print(f"📊 Total de logs: {result['total_logs']}")
            
            # Mostrar alguns logs se existirem
            if result['logs']:
                print("\n📋 Primeiros logs encontrados:")
                for i, log in enumerate(result['logs'][:3]):  # Mostrar apenas os 3 primeiros
                    print(f"  {i+1}. User ID: {log.get('user_id')}, Time: {log.get('time')}, Event: {log.get('event')}")
        else:
            print(f"❌ Erro: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

def iniciar_coleta_automatica(intervalo=30):
    """Inicia a coleta automática de logs"""
    print(f"\n=== INICIANDO COLETA AUTOMÁTICA (intervalo: {intervalo}s) ===")
    
    url = f"{BASE_URL}?dashboard/api/control-id/logs/coleta/"
    data = {
        "action": "start",
        "interval": intervalo,
        "control_id_ip": CONTROL_ID_IP
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            if 'config' in result:
                print(f"⚙️ Configuração: {result['config']}")
            else:
                print("⚙️ Configuração não retornada")
        else:
            print(f"❌ Erro: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

def verificar_status_coleta():
    """Verifica o status da coleta automática"""
    print("\n=== VERIFICANDO STATUS DA COLETA ===")

    url = f"{BASE_URL}/dashboard/api/control-id/logs/coleta/"

    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🔄 Ativo: {result.get('active', 'N/A')}")
            print(f"🧵 Thread viva: {result.get('thread_alive', 'N/A')}")
            if 'config' in result:
                print(f"⚙️ Configuração: {result['config']}")
            else:
                print("⚙️ Configuração não disponível")
        else:
            print(f"❌ Erro: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

def parar_coleta_automatica():
    """Para a coleta automática de logs"""
    print("\n=== PARANDO COLETA AUTOMÁTICA ===")
    
    url = f"{BASE_URL}/dashboard/api/control-id/logs/coleta/"
    data = {"action": "stop"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Erro: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

def main():
    """Função principal de teste"""
    print("🎯 TESTADOR DE COLETA DE LOGS DO CONTROL ID")
    print("=" * 50)
    
    # 1. Teste de coleta manual
    testar_coleta_manual()
    
    # 2. Iniciar coleta automática
    iniciar_coleta_automatica(30)  # A cada 30 segundos
    
    # 3. Verificar status
    time.sleep(2)  # Aguardar um pouco
    verificar_status_coleta()
    
    # 4. Aguardar um pouco para ver a coleta funcionando
    print("\n⏳ Aguardando 60 segundos para ver a coleta automática funcionando...")
    print("   (Você verá logs no console do Django se houver dados)")
    time.sleep(60)
    
    # 5. Verificar status novamente
    verificar_status_coleta()
    
    # 6. Parar coleta automática
    parar_coleta_automatica()
    
    print("\n✅ Teste concluído!")
    print("\n📝 COMO USAR:")
    print("1. Coleta manual: POST /api/control-id/logs/manual/")
    print("2. Iniciar automática: POST /api/control-id/logs/coleta/ {'action': 'start', 'interval': 30}")
    print("3. Status: GET /api/control-id/logs/coleta/")
    print("4. Parar: POST /api/control-id/logs/coleta/ {'action': 'stop'}")

if __name__ == "__main__":
    main()
