#!/usr/bin/env python3
"""
Comando Django para controlar o startup automático da coleta de logs
"""

from django.core.management.base import BaseCommand
from core.views import (
    log_collector_active, 
    log_collector_thread, 
    log_collector_config,
    iniciar_coleta_automatica_startup,
    parar_coleta_automatica_shutdown
)


class Command(BaseCommand):
    help = 'Controla o startup automático da coleta de logs'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['status', 'start', 'stop', 'restart'],
            help='Ação a ser executada'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'status':
            self.show_startup_status()
        elif action == 'start':
            self.start_startup_collection()
        elif action == 'stop':
            self.stop_startup_collection()
        elif action == 'restart':
            self.restart_startup_collection()

    def show_startup_status(self):
        """Mostra o status do startup automático"""
        global log_collector_active, log_collector_thread, log_collector_config
        
        self.stdout.write(
            self.style.HTTP_INFO('📊 STATUS DO STARTUP AUTOMÁTICO')
        )
        
        if log_collector_active:
            status_text = "🟢 ATIVO (iniciado automaticamente)"
        else:
            status_text = "🔴 INATIVO"
        
        thread_status = "🟢 RODANDO" if (log_collector_thread and log_collector_thread.is_alive()) else "🔴 PARADA"
        
        self.stdout.write(f'   🔄 Status: {status_text}')
        self.stdout.write(f'   🧵 Thread: {thread_status}')
        self.stdout.write(f'   ⏱️ Intervalo: {log_collector_config.get("interval", "N/A")}s')
        self.stdout.write(f'   🌐 IP Control ID: {log_collector_config.get("control_id_ip", "N/A")}')
        self.stdout.write(f'   📊 Total coletado: {log_collector_config.get("total_collected", 0)}')
        self.stdout.write(f'   🕐 Última coleta: {log_collector_config.get("last_collection", "Nunca")}')
        
        self.stdout.write('\n📋 CONFIGURAÇÃO:')
        self.stdout.write('   ✅ Startup automático está HABILITADO')
        self.stdout.write('   ✅ A coleta iniciará automaticamente quando o servidor Django for ligado')
        self.stdout.write('   ✅ Intervalo padrão: 30 segundos')

    def start_startup_collection(self):
        """Inicia a coleta startup manualmente"""
        try:
            iniciar_coleta_automatica_startup()
            self.stdout.write(
                self.style.SUCCESS('✅ Coleta automática de startup iniciada manualmente!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao iniciar coleta: {str(e)}')
            )

    def stop_startup_collection(self):
        """Para a coleta startup"""
        try:
            parar_coleta_automatica_shutdown()
            self.stdout.write(
                self.style.SUCCESS('✅ Coleta automática de startup parada!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao parar coleta: {str(e)}')
            )

    def restart_startup_collection(self):
        """Reinicia a coleta startup"""
        try:
            self.stdout.write('🔄 Parando coleta...')
            parar_coleta_automatica_shutdown()
            
            import time
            time.sleep(2)  # Aguardar um pouco
            
            self.stdout.write('🔄 Iniciando coleta...')
            iniciar_coleta_automatica_startup()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Coleta automática reiniciada!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao reiniciar coleta: {str(e)}')
            )
