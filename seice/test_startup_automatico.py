#!/usr/bin/env python3
"""
Script para testar o inicio automático da coleta de logs
"""

import subprocess
import time
import requests
import sys
import signal
import os

def verificar_coleta_ativa():
    """Verifica se a coleta está ativa"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/control-id/logs/coleta/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('active', False), data.get('config', {})
        return False, {}
    except:
        return False, {}

def main():
    print("🚀 TESTE DE STARTUP AUTOMÁTICO - COLETA DE LOGS")
    print("=" * 60)
    
    print("📋 Este teste irá:")
    print("   1. Iniciar o servidor Django")
    print("   2. Aguardar 10 segundos para inicialização")
    print("   3. Verificar se a coleta automática iniciou")
    print("   4. Mostrar status por 30 segundos")
    print("   5. Parar o servidor")
    
    input("\n⏳ Pressione Enter para continuar...")
    
    # Iniciar servidor Django
    print("\n🔄 Iniciando servidor Django...")
    django_process = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "127.0.0.1:8000"],
        cwd="seice",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Aguardar inicialização
        print("⏳ Aguardando 10 segundos para inicialização completa...")
        time.sleep(10)
        
        # Verificar se o servidor está rodando
        print("🔍 Verificando se servidor está rodando...")
        try:
            response = requests.get("http://127.0.0.1:8000/api/control-id/logs/coleta/", timeout=5)
            print(f"✅ Servidor respondendo: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Servidor não está respondendo: {e}")
            return
        
        # Verificar coleta automática
        print("\n🔍 Verificando se a coleta automática iniciou...")
        ativo, config = verificar_coleta_ativa()
        
        if ativo:
            print("✅ SUCESSO! Coleta automática está ATIVA!")
            print(f"   ⏱️ Intervalo: {config.get('interval')}s")
            print(f"   🌐 IP: {config.get('control_id_ip')}")
            print(f"   📊 Total coletado: {config.get('total_collected', 0)}")
            print(f"   🕐 Última coleta: {config.get('last_collection', 'Nunca')}")
        else:
            print("❌ FALHA! Coleta automática NÃO está ativa!")
            print("   Isso pode indicar um problema na inicialização.")
        
        # Monitorar por 30 segundos
        print(f"\n📊 Monitorando por 30 segundos...")
        for i in range(6):  # 6 iterações de 5 segundos = 30 segundos
            time.sleep(5)
            ativo, config = verificar_coleta_ativa()
            
            if ativo:
                total = config.get('total_collected', 0)
                ultima = config.get('last_collection', 'Nunca')
                print(f"   {i*5+5}s: ✅ Ativo | Total: {total} | Última: {ultima}")
            else:
                print(f"   {i*5+5}s: ❌ Inativo")
        
        print("\n✅ Teste concluído!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
    
    finally:
        # Parar servidor Django
        print("\n🛑 Parando servidor Django...")
        django_process.terminate()
        
        try:
            django_process.wait(timeout=5)
            print("✅ Servidor parado com sucesso!")
        except subprocess.TimeoutExpired:
            print("⚠️ Forçando parada do servidor...")
            django_process.kill()
            django_process.wait()
    
    print("\n🏁 Teste finalizado!")
    print("\n📝 RESULTADO:")
    if ativo:
        print("✅ A coleta automática está funcionando corretamente!")
        print("   O sistema iniciará automaticamente quando o servidor for ligado.")
    else:
        print("❌ A coleta automática não está funcionando.")
        print("   Verifique os logs do Django para mais detalhes.")

if __name__ == "__main__":
    main()
