#!/usr/bin/env python3
"""
SISTEMA SIMPLES DE COLETA E REGISTRO DE PRESENÇAS
Coleta logs do Control ID e registra presenças automaticamente
VERSÃO 2: Processa apenas LOGS NOVOS + Eventos expandidos
"""

import requests
import json
import threading
import time
import logging
from datetime import datetime, date, timedelta
from django.utils.dateparse import parse_datetime
from .models import Estagiario, Presenca

logger = logging.getLogger(__name__)

# Configuração simples
CONTROL_ID_IP = "192.168.3.40:81"
INTERVALO_COLETA = 30  # segundos
coleta_ativa = False
thread_coleta = None

# Controle de logs já processados - GARANTIA DE UNICIDADE
ultimo_log_processado = {
    'timestamp': None,
    'log_id': None,
    'total_processados': 0
}

# Cache de logs já processados (evita reprocessamento)
logs_processados_cache = set()  # IDs únicos dos logs já processados
MAX_CACHE_SIZE = 1000  # Limitar tamanho do cache

# NOVO: Cache de estagiários processados neste ciclo (evita entrada+saída na mesma coleta)
estagiarios_processados_neste_ciclo = set()  # user_ids processados neste ciclo

def fazer_login_control_id():
    """Faz login no Control ID e retorna a sessão"""
    try:
        url = f"http://{CONTROL_ID_IP}/login.fcgi"
        response = requests.post(url, data={'login': 'admin', 'password': 'admin'}, timeout=10)
        if response.status_code == 200:
            return response.json().get('session')
    except:
        pass
    return None

def gerar_id_unico_log(log):
    """Gera um ID único para o log baseado em seus dados principais"""
    user_id = str(log.get('user_id', ''))
    timestamp = str(log.get('time', ''))
    event = str(log.get('event', ''))
    
    # Criar hash único baseado nos dados principais
    import hashlib
    dados_log = f"{user_id}|{timestamp}|{event}"
    log_id = hashlib.md5(dados_log.encode()).hexdigest()[:16]
    return log_id

def filtrar_logs_novos(logs):
    """Filtra apenas os logs que ainda não foram processados - COM GARANTIA DE UNICIDADE"""
    global ultimo_log_processado, logs_processados_cache
    
    if not logs:
        return []
    
    logs_novos = []
    ultimo_timestamp = ultimo_log_processado['timestamp']
    
    for log in logs:
        # Gerar ID único para este log
        log_id_unico = gerar_id_unico_log(log)
        
        # VERIFICAÇÃO 1: Se já foi processado (cache), pular
        if log_id_unico in logs_processados_cache:
            continue
        
        # Extrair timestamp do log
        log_timestamp = log.get('time')
        
        try:
            # Converter timestamp para comparação
            if isinstance(log_timestamp, str):
                try:
                    log_dt = parse_datetime(log_timestamp)
                    if not log_dt:
                        log_dt = datetime.strptime(log_timestamp, '%d/%m/%Y %H:%M:%S')
                except:
                    continue
            elif isinstance(log_timestamp, (int, float)):
                log_dt = datetime.fromtimestamp(log_timestamp)
            else:
                continue
            
            # VERIFICAÇÃO 2: Se é o primeiro processamento, marcar e pular (não processar histórico)
            if ultimo_timestamp is None:
                ultimo_log_processado['timestamp'] = log_dt
                ultimo_log_processado['log_id'] = log_id_unico
                continue
            
            # VERIFICAÇÃO 3: Se o log é mais recente que o último processado, é novo
            if log_dt > ultimo_timestamp:
                # Adicionar ID único do log
                log['_log_id_unico'] = log_id_unico
                logs_novos.append(log)
        
        except Exception as e:
            logger.error(f"❌ Erro ao processar timestamp do log: {e}")
            continue
    
    logger.info(f"🔍 Encontrados {len(logs_novos)} logs REALMENTE NOVOS de {len(logs)} totais")
    return logs_novos

def buscar_logs_recentes():
    """Busca logs recentes do Control ID"""
    try:
        # Fazer login
        session = fazer_login_control_id()
        if not session:
            logger.error("❌ Não conseguiu fazer login no Control ID")
            return []
        
        # Buscar logs
        url = f"http://{CONTROL_ID_IP}/load_objects.fcgi"
        response = requests.post(
            url,
            params={'session': session},
            headers={'Content-Type': 'application/json'},
            json={"object": "access_logs"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logs = data.get('access_logs', [])
            logger.info(f"✅ Coletados {len(logs)} logs do Control ID")
            return logs
        else:
            logger.error(f"❌ Erro ao buscar logs: {response.status_code}")
            return []
    
    except Exception as e:
        logger.error(f"❌ Erro na coleta: {str(e)}")
        return []

def analisar_eventos_control_id():
    """Analisa os eventos encontrados nos logs para mapear padrões"""
    try:
        # Buscar logs
        logs = buscar_logs_recentes()
        
        if not logs:
            logger.info("📭 Nenhum log para analisar")
            return
        
        # Contar eventos
        eventos = {}
        user_eventos = {}
        
        for log in logs:
            event = str(log.get('event', 'unknown'))
            user_id = str(log.get('user_id', 'unknown'))
            timestamp = log.get('time', 'unknown')
            
            # Contar eventos gerais
            if event not in eventos:
                eventos[event] = 0
            eventos[event] += 1
            
            # Mapear eventos por usuário
            if user_id not in user_eventos:
                user_eventos[user_id] = {}
            if event not in user_eventos[user_id]:
                user_eventos[user_id][event] = []
            user_eventos[user_id][event].append(timestamp)
        
        # Mostrar análise
        logger.info("🔍 ANÁLISE DE EVENTOS CONTROL ID:")
        logger.info(f"📊 Total de logs analisados: {len(logs)}")
        
        logger.info("📋 Eventos encontrados:")
        for event, count in sorted(eventos.items()):
            logger.info(f"   Event '{event}': {count} ocorrências")
        
        # Tentar identificar padrões de entrada/saída por usuário
        logger.info("👥 Padrões por usuário (primeiros 3):")
        for i, (user_id, user_events) in enumerate(list(user_eventos.items())[:3]):
            try:
                estagiario = Estagiario.objects.get(control_id_user_id=user_id, ativo=True)
                nome = estagiario.nome
            except:
                nome = f"User {user_id}"
            
            logger.info(f"   {nome}:")
            for event, timestamps in user_events.items():
                logger.info(f"     Event '{event}': {len(timestamps)} vezes")
        
        return eventos, user_eventos
    
    except Exception as e:
        logger.error(f"❌ Erro na análise: {str(e)}")
        return {}, {}

def processar_log_para_presenca(log):
    """Converte um log do Control ID em presença - PROCESSAMENTO ÚNICO GARANTIDO"""
    global logs_processados_cache
    
    try:
        # Verificar se o log tem ID único (deveria ter sido adicionado no filtro)
        log_id_unico = log.get('_log_id_unico')
        if not log_id_unico:
            log_id_unico = gerar_id_unico_log(log)
        
        # GARANTIA FINAL: Verificar se já foi processado
        if log_id_unico in logs_processados_cache:
            logger.warning(f"⚠️ Log {log_id_unico} já foi processado - PULANDO")
            return False
        
        # Extrair dados do log
        user_id = str(log.get('user_id', ''))
        timestamp = log.get('time')
        event = str(log.get('event', '')).lower()
        
        if not user_id or not timestamp:
            logger.warning(f"⚠️ Log incompleto: user_id={user_id}, timestamp={timestamp}")
            return False
        
        # Converter timestamp
        try:
            if isinstance(timestamp, str):
                log_datetime = parse_datetime(timestamp)
                if not log_datetime:
                    log_datetime = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
            else:
                log_datetime = datetime.fromtimestamp(timestamp)
        except Exception as e:
            logger.error(f"❌ Erro ao converter timestamp: {timestamp} - {e}")
            return False
        
        # Buscar estagiário
        try:
            estagiario = Estagiario.objects.get(control_id_user_id=user_id, ativo=True)
        except Estagiario.DoesNotExist:
            logger.warning(f"⚠️ Estagiário não encontrado para Control ID user_id: {user_id}")
            # MARCAR COMO PROCESSADO mesmo se estagiário não encontrado
            logs_processados_cache.add(log_id_unico)
            return False
        
        data_log = log_datetime.date()
        hora_log = log_datetime.time()
        
        logger.info(f"🔄 Processando [{log_id_unico}]: {estagiario.nome} - Event: {event} - {data_log} {hora_log} - Estado atual: {'PRESENTE' if estagiario.presente else 'AUSENTE'}")
        
        # ==============================
        # LÓGICA BASEADA NO CAMPO 'presente' DO ESTAGIÁRIO
        # ==============================
        
        sucesso = False
        
        # SE ESTÁ AUSENTE (default=False) → REGISTRAR ENTRADA (começar a trabalhar)
        if not estagiario.presente:
            logger.info(f"🟢 {estagiario.nome} está AUSENTE → Registrando ENTRADA")
            
            # Criar ou atualizar presença APENAS COM ENTRADA
            presenca, criada = Presenca.objects.get_or_create(
                estagiario=estagiario,
                data=data_log,
                defaults={
                    'entrada': hora_log,
                    'saida': None,  # SEM saída
                    'observacao': f'Entrada automática Control ID (Event: {event}) [ID: {log_id_unico}]'
                }
            )
            
            if not criada:
                # Atualizar presença existente APENAS com entrada
                presenca.entrada = hora_log
                presenca.saida = None  # Garantir que saída está limpa
                presenca.horas = None  # Limpar horas calculadas
                presenca.observacao = f'Entrada: {hora_log} (Event: {event}) [ID: {log_id_unico}]'
                presenca.save()
                logger.info(f"🔄 Presença atualizada - APENAS entrada")
            else:
                logger.info(f"📝 Nova presença criada - APENAS entrada")
            
            # Marcar estagiário como presente (trabalhando)
            estagiario.presente = True
            estagiario.save()
            logger.info(f"✅ ENTRADA REGISTRADA: {estagiario.nome} às {hora_log} - Agora TRABALHANDO")
            sucesso = True
        
        # SE ESTÁ PRESENTE (presente=True) → REGISTRAR SAÍDA (parar de trabalhar)
        else:
            logger.info(f"🔴 {estagiario.nome} está PRESENTE → Registrando SAÍDA")
            
            # Buscar presença para este dia
            try:
                presenca = Presenca.objects.get(estagiario=estagiario, data=data_log)
                
                # APENAS atualizar com saída
                presenca.saida = hora_log
                
                # Calcular horas trabalhadas se houver entrada válida
                if presenca.entrada and presenca.entrada != hora_log:
                    entrada_dt = datetime.combine(data_log, presenca.entrada)
                    saida_dt = datetime.combine(data_log, hora_log)
                    horas_trabalhadas = saida_dt - entrada_dt
                    
                    # Verificar se a saída é depois da entrada
                    if horas_trabalhadas.total_seconds() > 0:
                        hours = int(horas_trabalhadas.total_seconds() // 3600)
                        minutes = int((horas_trabalhadas.total_seconds() % 3600) // 60)
                        presenca.horas = f"{hours:02d}:{minutes:02d}"
                    else:
                        logger.warning(f"⚠️ Saída antes da entrada: {estagiario.nome}")
                        presenca.horas = "00:00"
                else:
                    presenca.horas = "00:00"
                
                presenca.observacao += f' | Saída: {hora_log} (Event: {event}) [ID: {log_id_unico}]'
                presenca.save()
                
            except Presenca.DoesNotExist:
                # Criar presença APENAS com saída (situação anômala)
                presenca = Presenca.objects.create(
                    estagiario=estagiario,
                    data=data_log,
                    entrada=None,  # SEM entrada
                    saida=hora_log,
                    horas="00:00",
                    observacao=f'Saída sem entrada detectada (Event: {event}) [ID: {log_id_unico}]'
                )
                logger.warning(f"⚠️ Criada presença APENAS com saída para {estagiario.nome}")
            
            # Marcar estagiário como ausente (não trabalhando)
            estagiario.presente = False
            estagiario.save()
            
            horas_trabalhadas_str = presenca.horas if presenca.horas else "00:00"
            logger.info(f"✅ SAÍDA REGISTRADA: {estagiario.nome} às {hora_log} - Trabalhou {horas_trabalhadas_str}h - Agora AUSENTE")
            sucesso = True
        
        # MARCAR LOG COMO PROCESSADO - GARANTIA DE NÃO REPROCESSAMENTO
        logs_processados_cache.add(log_id_unico)
        
        # Limitar tamanho do cache
        if len(logs_processados_cache) > MAX_CACHE_SIZE:
            # Remover os 100 mais antigos (aproximação)
            logs_antigos = list(logs_processados_cache)[:100]
            for log_antigo in logs_antigos:
                logs_processados_cache.discard(log_antigo)
        
        # Atualizar timestamp do último log processado
        global ultimo_log_processado
        ultimo_log_processado['timestamp'] = log_datetime
        ultimo_log_processado['log_id'] = log_id_unico
        
        return sucesso
    
    except Exception as e:
        logger.error(f"❌ Erro ao processar log: {str(e)}")
        # Marcar como processado mesmo em caso de erro para evitar loops
        if 'log_id_unico' in locals():
            logs_processados_cache.add(log_id_unico)
        return False

def registrar_presencas_dos_logs():
    """Função principal: busca logs NOVOS e registra presenças - PROCESSAMENTO SEQUENCIAL ÚNICO"""
    global ultimo_log_processado
    
    try:
        # Buscar todos os logs
        logs = buscar_logs_recentes()
        
        if not logs:
            logger.info("📭 Nenhum log encontrado")
            return
        
        # Filtrar apenas logs NOVOS (com garantia de unicidade)
        logs_novos = filtrar_logs_novos(logs)
        
        if not logs_novos:
            logger.info("📭 Nenhum log NOVO encontrado")
            return
        
        logger.info(f"🔄 Processando {len(logs_novos)} logs NOVOS ÚNICOS...")
        
        processados = 0
        entradas = 0
        saidas = 0
        
        # PROCESSAR UM LOG POR VEZ - SEQUENCIAL
        for i, log in enumerate(logs_novos):
            user_id = str(log.get('user_id', ''))
            log_id = log.get('_log_id_unico', 'sem-id')
            
            logger.info(f"📋 Processando log {i+1}/{len(logs_novos)} [ID: {log_id}]...")
            
            # Verificar estado antes do processamento
            estado_antes = None
            nome_estagiario = "Desconhecido"
            try:
                if user_id:
                    estagiario = Estagiario.objects.get(control_id_user_id=user_id, ativo=True)
                    estado_antes = estagiario.presente
                    nome_estagiario = estagiario.nome
            except:
                pass
            
            # Processar o log (função já tem proteção contra duplicatas)
            if processar_log_para_presenca(log):
                processados += 1
                
                # Verificar estado depois do processamento para contar corretamente
                try:
                    if user_id and estado_antes is not None:
                        estagiario = Estagiario.objects.get(control_id_user_id=user_id, ativo=True)
                        estado_depois = estagiario.presente
                        
                        # Se mudou de ausente para presente = entrada
                        if not estado_antes and estado_depois:
                            entradas += 1
                            logger.info(f"   ✅ {nome_estagiario}: AUSENTE → PRESENTE (ENTRADA)")
                        # Se mudou de presente para ausente = saída
                        elif estado_antes and not estado_depois:
                            saidas += 1
                            logger.info(f"   ✅ {nome_estagiario}: PRESENTE → AUSENTE (SAÍDA)")
                        else:
                            logger.info(f"   ⚠️ {nome_estagiario}: Estado não mudou (possível duplicata evitada)")
                except Exception as e:
                    logger.error(f"   ❌ Erro ao verificar mudança de estado: {e}")
                    entradas += 1  # Assumir entrada em caso de erro
            else:
                logger.info(f"   ⏭️ Log {log_id} não processado (duplicata ou erro)")
        
        # Atualizar contador total
        ultimo_log_processado['total_processados'] += processados
        
        if processados > 0:
            logger.info(f"🎉 RESUMO FINAL:")
            logger.info(f"   📊 Logs únicos processados: {processados}")
            logger.info(f"   📥 Entradas registradas: {entradas}")
            logger.info(f"   📤 Saídas registradas: {saidas}")
            logger.info(f"   � Total geral histórico: {ultimo_log_processado['total_processados']}")
            logger.info(f"   🧹 Cache de logs processados: {len(logs_processados_cache)} itens")
        else:
            logger.info("📝 Logs novos encontrados, mas nenhuma presença registrada (possíveis duplicatas evitadas)")
    
    except Exception as e:
        logger.error(f"❌ Erro geral: {str(e)}")

def loop_coleta_automatica():
    """Loop que roda em background coletando e registrando presenças"""
    global coleta_ativa
    
    logger.info("🚀 Iniciando coleta automática de presenças...")
    
    while coleta_ativa:
        try:
            logger.info("🔄 Coletando logs e registrando presenças...")
            registrar_presencas_dos_logs()
            
        except Exception as e:
            logger.error(f"❌ Erro no loop: {str(e)}")
        
        # Aguardar intervalo
        time.sleep(INTERVALO_COLETA)

def iniciar_coleta_automatica():
    """Inicia a coleta automática"""
    global coleta_ativa, thread_coleta
    
    if coleta_ativa:
        logger.info("⚠️ Coleta já está ativa")
        return
    
    coleta_ativa = True
    thread_coleta = threading.Thread(target=loop_coleta_automatica, daemon=True)
    thread_coleta.start()
    
    logger.info(f"✅ Coleta automática iniciada! (a cada {INTERVALO_COLETA}s)")

def parar_coleta_automatica():
    """Para a coleta automática"""
    global coleta_ativa
    coleta_ativa = False
    logger.info("🛑 Coleta automática parada")

def status_coleta():
    """Retorna o status da coleta"""
    global ultimo_log_processado, logs_processados_cache
    
    return {
        'ativa': coleta_ativa,
        'thread_viva': thread_coleta.is_alive() if thread_coleta else False,
        'intervalo': INTERVALO_COLETA,
        'control_id_ip': CONTROL_ID_IP,
        'ultimo_processamento': {
            'timestamp': ultimo_log_processado['timestamp'].isoformat() if ultimo_log_processado['timestamp'] else None,
            'total_processados': ultimo_log_processado['total_processados']
        },
        'cache_logs': {
            'total_logs_cache': len(logs_processados_cache),
            'max_cache_size': MAX_CACHE_SIZE
        }
    }

def resetar_controle_logs():
    """Reseta o controle de logs processados (para testes)"""
    global ultimo_log_processado, logs_processados_cache
    ultimo_log_processado = {
        'timestamp': None,
        'log_id': None,
        'total_processados': 0
    }
    logs_processados_cache.clear()
    logger.info("🔄 Controle de logs resetado - cache limpo - próxima execução processará tudo como novo")

