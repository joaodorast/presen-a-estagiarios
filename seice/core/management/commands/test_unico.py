#!/usr/bin/env python3
"""
Management command para testar processamento único
"""

from django.core.management.base import BaseCommand
from core.coleta_simples import registrar_presencas_dos_logs, resetar_controle_logs, status_coleta
from core.models import Estagiario, Presenca

class Command(BaseCommand):
    help = 'Testa processamento único de logs'

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE: PROCESSAMENTO ÚNICO DE LOGS ===")
        
        # 1. Resetar sistema
        self.stdout.write("\n1. RESETANDO SISTEMA...")
        resetar_controle_logs()
        
        # 2. Estado inicial
        self.stdout.write("\n2. ESTADO INICIAL DOS ESTAGIÁRIOS:")
        estagiarios = Estagiario.objects.filter(ativo=True)
        for est in estagiarios:
            self.stdout.write(f"  {est.nome}: presente={est.presente}")
        
        # 3. Primeira coleta
        self.stdout.write("\n3. PRIMEIRA COLETA...")
        registrar_presencas_dos_logs()
        
        # 4. Estado após primeira coleta
        self.stdout.write("\n4. ESTADO APÓS PRIMEIRA COLETA:")
        for est in estagiarios:
            est.refresh_from_db()
            self.stdout.write(f"  {est.nome}: presente={est.presente}")
        
        # 5. Segunda coleta (deve evitar duplicatas)
        self.stdout.write("\n5. SEGUNDA COLETA (deve evitar duplicatas)...")
        registrar_presencas_dos_logs()
        
        # 6. Status final
        status = status_coleta()
        self.stdout.write(f"\n6. CACHE: {status['cache_logs']['total_logs_cache']} logs processados")
        
        self.stdout.write("\n=== TESTE CONCLUÍDO ===")
