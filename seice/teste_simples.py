#!/usr/bin/env python3
"""
Script SIMPLES para testar a coleta de logs do Control ID
"""

import requests
import json

# Configurações
BASE_URL = "http://127.0.0.1:8000"

def testar_coleta_manual():
    """Testa a coleta manual de logs"""
    print("🔄 Testando coleta manual...")
    
    url = f"{BASE_URL}/api/control-id/logs/manual/"
    
    try:
        # Fazendo requisição POST sem dados no body
        response = requests.post(url, headers={'Content-Type': 'application/json'})
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            print(f"📊 Total de logs: {result['total_logs']}")
            
            if result['logs'] and len(result['logs']) > 0:
                print("\n📋 Primeiros 3 logs:")
                for i, log in enumerate(result['logs'][:3]):
                    print(f"  {i+1}. User: {log.get('user_id')}, Time: {log.get('time')}, Event: {log.get('event')}")
            else:
                print("📋 Nenhum log encontrado")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text[:200])
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def verificar_status():
    """Verifica o status da coleta automática"""
    print("\n🔍 Verificando status...")
    
    url = f"{BASE_URL}/api/control-id/logs/coleta/"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status da coleta:")
            print(f"   🔄 Ativo: {result.get('active')}")
            print(f"   🧵 Thread: {result.get('thread_alive')}")
            
            config = result.get('config', {})
            print(f"   ⏱️ Intervalo: {config.get('interval')}s")
            print(f"   🌐 IP Control ID: {config.get('control_id_ip')}")
            print(f"   📊 Total coletado: {config.get('total_collected')}")
            print(f"   🕐 Última coleta: {config.get('last_collection')}")
        else:
            print(f"❌ Erro: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def iniciar_coleta(intervalo=30):
    """Inicia a coleta automática"""
    print(f"\n▶️ Iniciando coleta automática (a cada {intervalo}s)...")
    
    url = f"{BASE_URL}/api/control-id/logs/coleta/"
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': 'dummy'  # Tentar contornar CSRF
    }
    data = {
        "action": "start",
        "interval": intervalo,
        "control_id_ip": "192.168.3.40:81"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Erro {response.status_code}: Provavelmente já está rodando")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def parar_coleta():
    """Para a coleta automática"""
    print("\n⏹️ Parando coleta automática...")
    
    url = f"{BASE_URL}/api/control-id/logs/coleta/"
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': 'dummy'
    }
    data = {"action": "stop"}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Erro: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    print("🎯 TESTADOR SIMPLES - COLETA DE LOGS CONTROL ID")
    print("=" * 50)
    
    # 1. Verificar status atual
    verificar_status()
    
    # 2. Teste de coleta manual
    testar_coleta_manual()
    
    # 3. Menu simples
    while True:
        print("\n" + "="*30)
        print("1 - Verificar status")
        print("2 - Coleta manual")
        print("3 - Iniciar automática")
        print("4 - Parar automática")
        print("0 - Sair")
        
        try:
            opcao = input("\nEscolha uma opção: ").strip()
            
            if opcao == "1":
                verificar_status()
            elif opcao == "2":
                testar_coleta_manual()
            elif opcao == "3":
                intervalo = input("Intervalo em segundos (padrão 30): ").strip()
                intervalo = int(intervalo) if intervalo.isdigit() else 30
                iniciar_coleta(intervalo)
            elif opcao == "4":
                parar_coleta()
            elif opcao == "0":
                print("👋 Saindo...")
                break
            else:
                print("❌ Opção inválida")
        
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
