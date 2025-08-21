#!/usr/bin/env python3
"""
Comando SUPER SIMPLES para presenças automáticas
"""

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Sistema SIMPLES de presenças automáticas'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['status', 'manual', 'start', 'stop', 'reset'],
            help='O que fazer'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'status':
            self.mostrar_status()
        elif action == 'manual':
            self.coleta_manual()
        elif action == 'start':
            self.iniciar_sistema()
        elif action == 'stop':
            self.parar_sistema()
        elif action == 'reset':
            self.resetar_controle()

    def mostrar_status(self):
        """Mostra status do sistema simples"""
        from core.coleta_simples import status_coleta
        
        self.stdout.write(
            self.style.HTTP_INFO('🎯 SISTEMA SIMPLES DE PRESENÇAS v2.0')
        )
        
        status = status_coleta()
        
        if status['ativa']:
            self.stdout.write('✅ Sistema ATIVO - Processando apenas LOGS NOVOS!')
        else:
            self.stdout.write('❌ Sistema INATIVO')
        
        self.stdout.write(f'🧵 Thread: {"✅ Rodando" if status["thread_viva"] else "❌ Parada"}')
        self.stdout.write(f'⏱️ Intervalo: {status["intervalo"]} segundos')
        self.stdout.write(f'🌐 Control ID: {status["control_id_ip"]}')
        
        ultimo = status.get('ultimo_processamento', {})
        self.stdout.write(f'� Total processado: {ultimo.get("total_processados", 0)}')
        self.stdout.write(f'🕐 Último processamento: {ultimo.get("timestamp", "Nunca")}')
        
        self.stdout.write('\n📋 Recursos v2.0:')
        self.stdout.write('   � Detecta apenas logs NOVOS')
        self.stdout.write('   📥 Identifica ENTRADA automaticamente')
        self.stdout.write('   📤 Identifica SAÍDA automaticamente')
        self.stdout.write('   ⏱️ Calcula horas trabalhadas')
        self.stdout.write('   🚫 Evita reprocessamento de logs antigos')

    def coleta_manual(self):
        """Executa coleta manual"""
        from core.coleta_simples import registrar_presencas_dos_logs
        
        self.stdout.write('🔄 Executando coleta manual...')
        
        try:
            registrar_presencas_dos_logs()
            self.stdout.write(
                self.style.SUCCESS('✅ Coleta manual concluída!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro: {str(e)}')
            )

    def iniciar_sistema(self):
        """Inicia o sistema"""
        from core.coleta_simples import iniciar_coleta_automatica
        
        try:
            iniciar_coleta_automatica()
            self.stdout.write(
                self.style.SUCCESS('✅ Sistema iniciado!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro: {str(e)}')
            )

    def parar_sistema(self):
        """Para o sistema"""
        from core.coleta_simples import parar_coleta_automatica
        
        try:
            parar_coleta_automatica()
            self.stdout.write(
                self.style.SUCCESS('✅ Sistema parado!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro: {str(e)}')
            )

    def resetar_controle(self):
        """Reseta o controle de logs"""
        from core.coleta_simples import resetar_controle_logs
        
        try:
            resetar_controle_logs()
            self.stdout.write(
                self.style.SUCCESS('✅ Controle de logs resetado! Próxima execução processará tudo como novo.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro: {str(e)}')
            )
