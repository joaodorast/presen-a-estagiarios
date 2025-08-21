#!/usr/bin/env python3
"""
Comando Django para controlar a coleta de logs do Control ID
"""

from django.core.management.base import BaseCommand
from core.views import (
    log_collector_active, 
    log_collector_thread, 
    log_collector_config,
    coletar_logs_control_id,
    obter_sessao_control_id
)
import threading
import requests
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Controla a coleta periódica de logs do Control ID'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['start', 'stop', 'status', 'manual', 'test'],
            help='Ação a ser executada'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Intervalo em segundos para coleta automática (padrão: 30)'
        )
        parser.add_argument(
            '--ip',
            default='192.168.3.40:81',
            help='IP do Control ID (padrão: 192.168.3.40:81)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'start':
            self.start_collection(options)
        elif action == 'stop':
            self.stop_collection()
        elif action == 'status':
            self.show_status()
        elif action == 'manual':
            self.manual_collection(options)
        elif action == 'test':
            self.test_connection(options)

    def start_collection(self, options):
        """Inicia a coleta automática"""
        global log_collector_active, log_collector_thread
        
        if log_collector_active:
            self.stdout.write(
                self.style.WARNING('⚠️ Coleta automática já está ativa!')
            )
            return
        
        # Configurar parâmetros
        log_collector_config['interval'] = options['interval']
        log_collector_config['control_id_ip'] = options['ip']
        
        # Iniciar thread
        log_collector_active = True
        log_collector_thread = threading.Thread(target=coletar_logs_control_id, daemon=True)
        log_collector_thread.start()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Coleta automática iniciada!\n'
                f'   ⏱️ Intervalo: {options["interval"]}s\n'
                f'   🌐 IP: {options["ip"]}'
            )
        )

    def stop_collection(self):
        """Para a coleta automática"""
        global log_collector_active
        
        if not log_collector_active:
            self.stdout.write(
                self.style.WARNING('⚠️ Coleta automática não está ativa!')
            )
            return
        
        log_collector_active = False
        self.stdout.write(
            self.style.SUCCESS('✅ Coleta automática parada!')
        )

    def show_status(self):
        """Mostra o status da coleta"""
        global log_collector_active, log_collector_thread, log_collector_config
        
        self.stdout.write(
            self.style.HTTP_INFO('📊 STATUS DA COLETA DE LOGS')
        )
        
        status = "🟢 ATIVA" if log_collector_active else "🔴 PARADA"
        thread_status = "🟢 VIVA" if (log_collector_thread and log_collector_thread.is_alive()) else "🔴 MORTA"
        
        self.stdout.write(f'   🔄 Status: {status}')
        self.stdout.write(f'   🧵 Thread: {thread_status}')
        self.stdout.write(f'   ⏱️ Intervalo: {log_collector_config.get("interval", "N/A")}s')
        self.stdout.write(f'   🌐 IP Control ID: {log_collector_config.get("control_id_ip", "N/A")}')
        self.stdout.write(f'   📊 Total coletado: {log_collector_config.get("total_collected", 0)}')
        self.stdout.write(f'   🕐 Última coleta: {log_collector_config.get("last_collection", "Nunca")}')

    def manual_collection(self, options):
        """Executa uma coleta manual"""
        self.stdout.write(
            self.style.HTTP_INFO('🔄 Executando coleta manual...')
        )
        
        try:
            # Obter sessão
            session_id = obter_sessao_control_id()
            if not session_id:
                self.stdout.write(
                    self.style.ERROR('❌ Não foi possível obter sessão do Control ID')
                )
                return
            
            # Fazer requisição aos logs
            url = f"http://{options['ip']}/load_objects.fcgi"
            params = {'session': session_id}
            headers = {'Content-Type': 'application/json'}
            payload = {"object": "access_logs"}
            
            response = requests.post(
                url,
                params=params,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logs_data = response.json()
                
                if 'access_logs' in logs_data:
                    logs = logs_data['access_logs']
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Coleta manual concluída!\n'
                            f'   📊 Total de logs: {len(logs)}\n'
                            f'   🕐 Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                        )
                    )
                    
                    # Mostrar alguns logs
                    if logs:
                        self.stdout.write('\n📋 Primeiros 5 logs:')
                        for i, log in enumerate(logs[:5]):
                            self.stdout.write(
                                f'   {i+1}. User: {log.get("user_id")}, '
                                f'Time: {log.get("time")}, '
                                f'Event: {log.get("event")}'
                            )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Nenhum log encontrado na resposta')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Erro na API Control ID: {response.status_code}\n'
                        f'   Detalhes: {response.text[:200]}'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro na coleta manual: {str(e)}')
            )

    def test_connection(self, options):
        """Testa a conexão com o Control ID"""
        self.stdout.write(
            self.style.HTTP_INFO(f'🔍 Testando conexão com {options["ip"]}...')
        )
        
        try:
            # Testar login
            session_id = obter_sessao_control_id()
            if session_id:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Conexão OK!\n'
                        f'   🔑 Session ID: {session_id[:20]}...\n'
                        f'   🌐 IP: {options["ip"]}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Falha no login do Control ID')
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro na conexão: {str(e)}')
            )
