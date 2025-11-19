# #!/usr/bin/env python3
# """
# SISTEMA SIMPLES DE COLETA E REGISTRO DE PRESENÇAS
# Coleta logs do Control ID e registra presenças automaticamente
# VERSÃO 3.0: Baseado na existência de instância de Presença ao invés do campo 'presente'
# """

# import requests
# import json
# import threading
# import time
# import logging
# from datetime import datetime, date, timedelta
# from django.utils.dateparse import parse_datetime
# from django.utils import timezone
# from .models import Estagiario, Presenca, ControleColetaLogs, Sensor

# logger = logging.getLogger(__name__)

# ultimas_acoes = {}  # {user_id: datetime}
# TIME_DELTA_IGNORAR = timedelta(seconds=5)

# def get_controle_coleta(sensor):
#     """Obtém ou cria a instância de ControleColetaLogs para o sensor"""
#     try:
#         controle = ControleColetaLogs.objects.get(sensor=sensor)
#     except ControleColetaLogs.DoesNotExist:
#         controle = ControleColetaLogs.objects.create(sensor=sensor)
#     return controle

# # Configuração simples
# CONTROL_ID_IP = "192.168.3.40:81"
# INTERVALO_COLETA = 30  # segundos
# coleta_ativa = False
# thread_coleta = None

# # Controle de logs já processados - GARANTIA DE UNICIDADE
# ultimo_log_processado = {
#     'timestamp': None,
#     'log_id': None,
#     'total_processados': 0
# }

# # Cache de logs já processados (evita reprocessamento)
# logs_processados_cache = set()  # IDs únicos dos logs já processados
# MAX_CACHE_SIZE = 1000  # Limitar tamanho do cache

# # NOVO: Cache de estagiários processados neste ciclo (evita entrada+saída na mesma coleta)
# estagiarios_processados_neste_ciclo = set()  # user_ids processados neste ciclo
# # NOVO: Timeout para o cache de processamento por ciclo (limpar a cada X minutos)
# TIMEOUT_CACHE_CICLO = 300  # 5 minutos
# ultimo_reset_cache_ciclo = datetime.now()

# def fazer_login_control_id(sensor):
#     """Faz login no Control ID do sensor especificado e retorna a sessão"""
#     try:
#         url = f"http://{sensor.ip}:{sensor.porta}/login.fcgi"
#         response = requests.post(url, data={'login': 'admin', 'password': 'admin'}, timeout=10)
#         if response.status_code == 200:
#             return response.json().get('session')
#     except:
#         pass
#     return None

# def gerar_id_unico_log(log):
#     """Gera um ID único para o log baseado em seus dados principais"""
#     user_id = str(log.get('user_id', ''))
#     timestamp = str(log.get('time', ''))
#     event = str(log.get('event', ''))

#     # Criar hash único baseado nos dados principais
#     import hashlib
#     dados_log = f"{user_id}|{timestamp}|{event}"
#     log_id = hashlib.md5(dados_log.encode()).hexdigest()[:16]
#     return log_id

# def gerar_id_unico_log_sensor(log, sensor):
#     """Gera um ID único para o log baseado em seus dados principais incluindo o sensor"""
#     user_id = str(log.get('user_id', ''))
#     timestamp = str(log.get('time', ''))
#     event = str(log.get('event', ''))
#     sensor_id = str(sensor.id)

#     # Criar hash único baseado nos dados principais incluindo o sensor
#     import hashlib
#     dados_log = f"{sensor_id}|{user_id}|{timestamp}|{event}"
#     log_id = hashlib.md5(dados_log.encode()).hexdigest()[:16]
#     return log_id

# def resetar_cache_ciclo_se_necessario():
#     """Reseta o cache de processamento por ciclo após timeout"""
#     global ultimo_reset_cache_ciclo, estagiarios_processados_neste_ciclo
    
#     agora = datetime.now()
#     if (agora - ultimo_reset_cache_ciclo).total_seconds() > TIMEOUT_CACHE_CICLO:
#         logger.info(f"🧹 Resetando cache de ciclo após {TIMEOUT_CACHE_CICLO}s")
#         estagiarios_processados_neste_ciclo.clear()
#         ultimo_reset_cache_ciclo = agora

# def verificar_status_estagiario_no_dia(estagiario, data_verificacao):
#     """
#     NOVA LÓGICA: Verifica o status do estagiário baseado na existência de presença no banco
#     Retorna: 'ausente', 'presente', 'completo'
#     """
#     try:
#         # Buscar presença do estagiário para o dia específico
#         presenca = Presenca.objects.filter(
#             estagiario=estagiario,
#             data=data_verificacao
#         ).first()
        
#         if not presenca:
#             # Não tem registro de presença = AUSENTE
#             return 'ausente'
        
#         if presenca.entrada and presenca.saida:
#             # Tem entrada E saída = COMPLETO (não processar mais)
#             return 'completo'
        
#         if presenca.entrada and not presenca.saida:
#             # Tem entrada mas não tem saída = PRESENTE
#             return 'presente'
        
#         if not presenca.entrada and presenca.saida:
#             # Caso anômalo: só tem saída = tratar como AUSENTE
#             logger.warning(f"⚠️ {estagiario.nome} tem apenas saída sem entrada em {data_verificacao}")
#             return 'ausente'
        
#         # Registro existe mas sem entrada nem saída = tratar como AUSENTE
#         return 'ausente'
        
#     except Exception as e:
#         logger.error(f"❌ Erro ao verificar status de {estagiario.nome}: {e}")
#         return 'ausente'

# def filtrar_logs_novos(logs, sensor):
#     """Filtra apenas os logs que ainda não foram processados - COM GARANTIA DE UNICIDADE"""
#     controle = get_controle_coleta(sensor)
#     logs_processados_cache = set(controle.processed_log_ids)

#     if not logs:
#         return []

#     logs_novos = []
#     ultimo_timestamp = controle.ultimo_timestamp

#     for log in logs:
#         # Gerar ID único para este log incluindo o sensor
#         log_id_unico = gerar_id_unico_log_sensor(log, sensor)

#         # VERIFICAÇÃO 1: Se já foi processado (cache), pular
#         if log_id_unico in logs_processados_cache:
#             continue

#         # Extrair timestamp do log
#         log_timestamp = log.get('time')

#         try:
#             # Converter timestamp para comparação - GARANTIR TIMEZONE CONSISTENCY
#             if isinstance(log_timestamp, str):
#                 try:
#                     log_dt = parse_datetime(log_timestamp)
#                     if not log_dt:
#                         log_dt = datetime.strptime(log_timestamp, '%d/%m/%Y %H:%M:%S')
#                     # GARANTIR QUE SEMPRE SEJA TIMEZONE-NAIVE
#                     if timezone.is_aware(log_dt):
#                         log_dt = timezone.make_naive(log_dt)
#                     # Adicionar offset UTC+3 se ainda não foi adicionado
#                     log_dt = log_dt + timedelta(hours=3)
#                 except:
#                     continue
#             elif isinstance(log_timestamp, (int, float)):
#                 log_dt = datetime.fromtimestamp(log_timestamp) + timedelta(hours=3)
#             else:
#                 continue

#             # VERIFICAÇÃO 2: Se é o primeiro processamento, marcar e pular (não processar histórico)
#             if ultimo_timestamp is None:
#                 controle.ultimo_timestamp = log_dt
#                 controle.ultimo_log_id = log_id_unico
#                 controle.save()
#                 continue

#             # VERIFICAÇÃO 3: Se o log é mais recente que o último processado, é novo
#             # GARANTIR QUE AMBOS SEJAM TIMEZONE-NAIVE PARA COMPARAÇÃO
#             if timezone.is_aware(ultimo_timestamp):
#                 ultimo_timestamp_naive = timezone.make_naive(ultimo_timestamp)
#             else:
#                 ultimo_timestamp_naive = ultimo_timestamp

#             # GARANTIR QUE log_dt TAMBÉM SEJA NAIVE ANTES DA COMPARAÇÃO
#             if timezone.is_aware(log_dt):
#                 log_dt_naive = timezone.make_naive(log_dt)
#             else:
#                 log_dt_naive = log_dt

#             if log_dt_naive > ultimo_timestamp_naive:
#                 # Adicionar ID único do log
#                 log['_log_id_unico'] = log_id_unico
#                 logs_novos.append(log)

#         except Exception as e:
#             logger.error(f"❌ Erro ao processar timestamp do log: {e}")
#             continue

#     logger.info(f"🔍 [{sensor.nome}] Encontrados {len(logs_novos)} logs REALMENTE NOVOS de {len(logs)} totais")
#     return logs_novos

# def buscar_logs_recentes(sensor):
#     """Busca logs recentes do Control ID do sensor especificado"""
#     try:
#         # Fazer login no sensor específico
#         session = fazer_login_control_id(sensor)
#         if not session:
#             logger.error(f"❌ Não conseguiu fazer login no sensor {sensor.nome} ({sensor.ip}:{sensor.porta})")
#             return []

#         # Buscar logs
#         url = f"http://{sensor.ip}:{sensor.porta}/load_objects.fcgi"
#         response = requests.post(
#             url,
#             params={'session': session},
#             headers={'Content-Type': 'application/json'},
#             json={"object": "access_logs"},
#             timeout=30
#         )

#         if response.status_code == 200:
#             data = response.json()
#             logs = data.get('access_logs', [])
#             logger.info(f"✅ [{sensor.nome}] Coletados {len(logs)} logs do Control ID")
#             return logs
#         else:
#             logger.error(f"❌ [{sensor.nome}] Erro ao buscar logs: {response.status_code}")
#             return []

#     except Exception as e:
#         logger.error(f"❌ [{sensor.nome}] Erro na coleta: {str(e)}")
#         return []

# def processar_log_para_presenca(log, sensor):
#     """Converte um log do Control ID em presença - NOVA LÓGICA BASEADA NA EXISTÊNCIA DE PRESENÇA"""
#     global estagiarios_processados_neste_ciclo

#     controle = get_controle_coleta(sensor)
#     logs_processados_cache = set(controle.processed_log_ids)

#     try:
#         # Verificar se o log tem ID único (deveria ter sido adicionado no filtro)
#         log_id_unico = log.get('_log_id_unico')
#         if not log_id_unico:
#             log_id_unico = gerar_id_unico_log(log)

#         # GARANTIA FINAL: Verificar se já foi processado
#         if log_id_unico in logs_processados_cache:
#             logger.warning(f"⚠️ Log {log_id_unico} já foi processado - PULANDO")
#             return False

#         # MARCAR COMO PROCESSADO IMEDIATAMENTE para evitar reprocessamento
#         logs_processados_cache.add(log_id_unico)
        
#         # Extrair dados do log
#         user_id = str(log.get('user_id', ''))
#         timestamp = log.get('time')
#         event = str(log.get('event', '')).lower()
        
#         if not user_id or not timestamp:
#             logger.warning(f"⚠️ Log incompleto: user_id={user_id}, timestamp={timestamp}")
#             return False
        
#         # NOVA VERIFICAÇÃO: Se o estagiário já foi processado neste ciclo, aguardar próximo ciclo
#         if user_id in estagiarios_processados_neste_ciclo:
#             logger.info(f"⏳ {user_id} já processado neste ciclo - aguardando próximo ciclo para evitar redundância")
#             return False
        
#         # Converter timestamp - GARANTIR TIMEZONE CONSISTENCY
#         try:
#             if isinstance(timestamp, str):
#                 log_datetime = parse_datetime(timestamp)
#                 if not log_datetime:
#                     log_datetime = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
#                 # Se o timestamp é timezone-aware, converter para naive antes de adicionar offset
#                 if timezone.is_aware(log_datetime):
#                     log_datetime = timezone.make_naive(log_datetime)
#                 log_datetime = log_datetime + timedelta(hours=3)
#             else:
#                 log_datetime = datetime.fromtimestamp(timestamp) + timedelta(hours=3)
#         except Exception as e:
#             logger.error(f"❌ Erro ao converter timestamp: {timestamp} - {e}")
#             return False
        
#         # Buscar estagiário
#         try:
#             estagiario = Estagiario.objects.get(control_id_user_id=user_id, ativo=True)
#         except Estagiario.DoesNotExist:
#             logger.warning(f"⚠️ Estagiário não encontrado para Control ID user_id: {user_id}")
#             return False
        
#         data_log = log_datetime.date()
#         hora_log = log_datetime.time()
        
#         # NOVA LÓGICA: Verificar status baseado na existência de presença no banco
#         status_atual = verificar_status_estagiario_no_dia(estagiario, data_log)
        
#         logger.info(f"🔄 Processando [{log_id_unico}]: {estagiario.nome} - Event: {event} - {data_log} {hora_log} - Status: {status_atual.upper()}")
        
#         # Se já tem entrada e saída completas, ignorar
#         if status_atual == 'completo':
#             logger.info(f"⏭️ {estagiario.nome} já tem entrada e saída completas para {data_log}, ignorando log.")
#             # Marcar o log como processado para evitar reprocessamento
#             logs_processados_cache.add(log_id_unico)
#             # Atualizar controle imediatamente para logs ignorados
#             controle.processed_log_ids = list(logs_processados_cache)
#             controle.save()
#             return False
        
#         # ==============================
#         # NOVA LÓGICA BASEADA NO STATUS DA PRESENÇA NO BANCO
#         # ==============================
        
#         sucesso = False

#         ultima_acao = ultimas_acoes.get(user_id)
#         if ultima_acao and abs((log_datetime - ultima_acao).total_seconds()) < 5:
#             logger.info(f"⚠️ Ignorado log duplicado para {estagiario.nome} no mesmo segundo ({log_datetime})")
#             return False
        
#         # SE ESTÁ AUSENTE (não tem presença ou só tem saída) → REGISTRAR ENTRADA
#         if status_atual == 'ausente':
#             logger.info(f"🟢 {estagiario.nome} está AUSENTE → Registrando ENTRADA")
#             presenca, criada = Presenca.objects.get_or_create(
#                 estagiario=estagiario,
#                 data=data_log,
#                 defaults={
#                     'entrada': hora_log,
#                     'saida': None,
#                     'observacao': f'Entrada automática Control ID'
#                 }
#             )
#             if not criada:
#                 # Atualizar entrada se não existe ainda
#                 if not presenca.entrada:
#                     presenca.entrada = hora_log
#                 presenca.saida = None
#                 presenca.horas = None
#                 presenca.observacao = f'Entrada automática Control ID'
#                 presenca.save()
#                 logger.info(f"🔄 Presença atualizada - ENTRADA registrada")
#             else:
#                 logger.info(f"📝 Nova presença criada - ENTRADA registrada")
            
#             logger.info(f"✅ ENTRADA REGISTRADA: {estagiario.nome} às {hora_log}")
#             sucesso = True
            
#         # SE ESTÁ PRESENTE (tem entrada sem saída) → REGISTRAR SAÍDA
#         elif status_atual == 'presente':
#             logger.info(f"🔴 {estagiario.nome} está PRESENTE → Registrando SAÍDA")
#             try:
#                 presenca = Presenca.objects.get(estagiario=estagiario, data=data_log)
#                 if not presenca.saida:  # Só registrar saída se não tem ainda
#                     presenca.saida = hora_log
#                     # Calcular horas trabalhadas
#                     if presenca.entrada and presenca.entrada != hora_log:
#                         entrada_dt = datetime.combine(data_log, presenca.entrada)
#                         saida_dt = datetime.combine(data_log, hora_log)
#                         horas_trabalhadas = saida_dt - entrada_dt
#                         if horas_trabalhadas.total_seconds() > 0:
#                             hours = int(horas_trabalhadas.total_seconds() // 3600)
#                             minutes = int((horas_trabalhadas.total_seconds() % 3600) // 60)
#                             presenca.horas = f"{hours:02d}:{minutes:02d}"
#                         else:
#                             logger.warning(f"⚠️ Saída antes da entrada: {estagiario.nome}")
#                             presenca.horas = "00:00"
#                     else:
#                         presenca.horas = "00:00"
#                     presenca.observacao = f'Saída automática Control ID'
#                     presenca.save()
                    
#                     horas_trabalhadas_str = presenca.horas if presenca.horas else "00:00"
#                     logger.info(f"✅ SAÍDA REGISTRADA: {estagiario.nome} às {hora_log} - Trabalhou {horas_trabalhadas_str}h")
#                     sucesso = True
#                 else:
#                     logger.info(f"⚠️ {estagiario.nome} já tem saída registrada para {data_log}")
                    
#             except Presenca.DoesNotExist:
#                 # Caso anômalo: verificação disse que estava presente mas não tem registro
#                 logger.error(f"❌ Inconsistência: {estagiario.nome} detectado como presente mas sem registro de presença")
#                 return False
        
#         # MARCAR ESTAGIÁRIO COMO PROCESSADO NESTE CICLO
#         estagiarios_processados_neste_ciclo.add(user_id)

#         # Atualizar controle
#         controle.ultimo_timestamp = log_datetime
#         controle.ultimo_log_id = log_id_unico
#         controle.processed_log_ids = list(logs_processados_cache)
#         controle.save()

#         ultimas_acoes[user_id] = log_datetime

#         return sucesso
    
#     except Exception as e:
#         logger.error(f"❌ Erro ao processar log: {str(e)}")
#         return False

# def registrar_presencas_dos_logs(sensor):
#     """Função principal: busca logs NOVOS e registra presenças - PROCESSAMENTO SEQUENCIAL ÚNICO"""
#     global ultimo_log_processado, logs_processados_cache

#     # Reset do cache de ciclo se necessário
#     resetar_cache_ciclo_se_necessario()

#     # Buscar todos os logs
#     try:
#         logs = buscar_logs_recentes(sensor)
#     except Exception as e:
#         logger.error(f"❌ Erro ao buscar logs: {str(e)}")
#         return

#     if not logs:
#         logger.info("📭 Nenhum log encontrado")
#         return

#     # Filtrar apenas logs NOVOS (com garantia de unicidade)
#     try:
#         logs_novos = filtrar_logs_novos(logs, sensor)
#     except Exception as e:
#         logger.error(f"❌ Erro ao filtrar logs novos: {str(e)}")
#         return

#     if not logs_novos:
#         logger.info("📭 Nenhum log NOVO encontrado")
#         return

#     # Ordenar logs por timestamp para processar em ordem cronológica
#     try:
#         logs_novos.sort(key=lambda x: x.get('time', ''), reverse=False)
#     except:
#         logger.warning("⚠️ Não foi possível ordenar logs por timestamp")

#     logger.info(f"🔄 Processando {len(logs_novos)} logs NOVOS ÚNICOS...")

#     processados = 0
#     entradas = 0
#     saidas = 0

#     # PROCESSAR UM LOG POR VEZ - SEQUENCIAL E ORDENADO
#     for i, log in enumerate(logs_novos):
#         user_id = str(log.get('user_id', ''))
#         log_id = log.get('_log_id_unico', 'sem-id')

#         logger.info(f"📋 Processando log {i+1}/{len(logs_novos)} [ID: {log_id}]...")

#         # Verificar estado antes do processamento (baseado na presença no banco)
#         status_antes = None
#         nome_estagiario = "Desconhecido"
#         try:
#             if user_id:
#                 estagiario = Estagiario.objects.get(control_id_user_id=user_id, ativo=True)
#                 timestamp = log.get('time')
#                 if isinstance(timestamp, str):
#                     log_datetime = parse_datetime(timestamp)
#                     if not log_datetime:
#                         log_datetime = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
#                     # Se o timestamp é timezone-aware, converter para naive
#                     if timezone.is_aware(log_datetime):
#                         log_datetime = timezone.make_naive(log_datetime)
#                 else:
#                     log_datetime = datetime.fromtimestamp(timestamp)
#                 data_log = log_datetime.date()
#                 status_antes = verificar_status_estagiario_no_dia(estagiario, data_log)
#                 nome_estagiario = estagiario.nome
#         except Exception:
#             pass

#         # Processar o log
#         if processar_log_para_presenca(log, sensor):
#             processados += 1

#             # Verificar estado depois do processamento para contar corretamente
#             try:
#                 if user_id and status_antes:
#                     estagiario = Estagiario.objects.get(control_id_user_id=user_id, ativo=True)
#                     status_depois = verificar_status_estagiario_no_dia(estagiario, data_log)

#                     # Se mudou de ausente para presente = entrada
#                     if status_antes == 'ausente' and status_depois == 'presente':
#                         entradas += 1
#                         logger.info(f"   ✅ {nome_estagiario}: AUSENTE → PRESENTE (ENTRADA)")
#                     # Se mudou de presente para completo = saída
#                     elif status_antes == 'presente' and status_depois == 'completo':
#                         saidas += 1
#                         logger.info(f"   ✅ {nome_estagiario}: PRESENTE → COMPLETO (SAÍDA)")
#                     else:
#                         logger.info(f"   ⚠️ {nome_estagiario}: Status não mudou conforme esperado ({status_antes} → {status_depois})")
#             except Exception as e:
#                 logger.error(f"   ❌ Erro ao verificar mudança de estado: {e}")
#         else:
#             logger.info(f"   ⏭️ Log {log_id} não processado (duplicata, erro ou aguardando próximo ciclo)")

#     # Atualizar contador total
#     controle = get_controle_coleta(sensor)
#     controle.total_processados += processados

#     # Limitar tamanho do cache após processamento
#     if len(controle.processed_log_ids) > MAX_CACHE_SIZE:
#         controle.processed_log_ids = controle.processed_log_ids[100:]  # Remove os primeiros 100

#     controle.save()

#     if processados > 0:
#         logger.info(f"🎉 RESUMO FINAL:")
#         logger.info(f"   📊 Logs únicos processados: {processados}")
#         logger.info(f"   📥 Entradas registradas: {entradas}")
#         logger.info(f"   📤 Saídas registradas: {saidas}")
#         logger.info(f"   📈 Total geral histórico: {ultimo_log_processado['total_processados']}")
#         logger.info(f"   🧹 Cache de logs processados: {len(logs_processados_cache)} itens")
#         logger.info(f"   👥 Estagiários processados neste ciclo: {len(estagiarios_processados_neste_ciclo)}")
#     else:
#         logger.info("📝 Logs novos encontrados, mas nenhuma presença registrada (duplicatas evitadas ou aguardando próximo ciclo)")

# def loop_coleta_automatica():
#     """Loop que roda em background coletando e registrando presenças para todos os sensores"""
#     global coleta_ativa

#     logger.info("🚀 Iniciando coleta automática de presenças (NOVA VERSÃO - baseada na existência de presença)...")

#     while coleta_ativa:
#         try:
#             logger.info("🔄 Coletando logs e registrando presenças para todos os sensores...")

#             # Processar logs para cada sensor ativo
#             sensores = Sensor.objects.filter(ativo=True)
#             for sensor in sensores:
#                 logger.info(f"📡 Processando sensor: {sensor.nome}")
#                 registrar_presencas_dos_logs(sensor)

#         except Exception as e:
#             logger.error(f"❌ Erro no loop: {str(e)}")

#         # Aguardar intervalo
#         time.sleep(INTERVALO_COLETA)

# def iniciar_coleta_automatica():
#     """Inicia a coleta automática"""
#     global coleta_ativa, thread_coleta
    
#     if coleta_ativa:
#         logger.info("⚠️ Coleta já está ativa")
#         return
    
#     coleta_ativa = True
#     thread_coleta = threading.Thread(target=loop_coleta_automatica, daemon=True)
#     thread_coleta.start()
    
#     logger.info(f"✅ Coleta automática iniciada! (a cada {INTERVALO_COLETA}s) - VERSÃO 3.0")

# def parar_coleta_automatica():
#     """Para a coleta automática"""
#     global coleta_ativa
#     coleta_ativa = False
#     logger.info("🛑 Coleta automática parada")

# def status_coleta():
#     """Retorna o status da coleta para todos os sensores"""
#     global estagiarios_processados_neste_ciclo

#     sensores_status = []
#     sensores = Sensor.objects.all()
#     for sensor in sensores:
#         controle = get_controle_coleta(sensor)
#         sensores_status.append({
#             'sensor_nome': sensor.nome,
#             'sensor_ip': sensor.ip,
#             'sensor_porta': sensor.porta,
#             'ativo': sensor.ativo,
#             'ultimo_processamento': {
#                 'timestamp': controle.ultimo_timestamp.isoformat() if controle.ultimo_timestamp else None,
#                 'total_processados': controle.total_processados
#             },
#             'cache_logs': {
#                 'total_logs_cache': len(controle.processed_log_ids),
#                 'max_cache_size': MAX_CACHE_SIZE
#             }
#         })

#     return {
#         'ativa': coleta_ativa,
#         'thread_viva': thread_coleta.is_alive() if thread_coleta else False,
#         'intervalo': INTERVALO_COLETA,
#         'versao': '3.0 - Baseada na existência de presença (Multi-sensor)',
#         'sensores': sensores_status,
#         'cache_ciclo': {
#             'estagiarios_processados_neste_ciclo': len(estagiarios_processados_neste_ciclo),
#             'timeout_cache_ciclo': TIMEOUT_CACHE_CICLO,
#             'ultimo_reset': ultimo_reset_cache_ciclo.isoformat() if ultimo_reset_cache_ciclo else None
#         }
#     }

# def resetar_controle_logs():
#     """Reseta o controle de logs processados (para testes)"""
#     global estagiarios_processados_neste_ciclo

#     controle = get_controle_coleta()
#     controle.ultimo_timestamp = None
#     controle.ultimo_log_id = None
#     controle.total_processados = 0
#     controle.processed_log_ids = []
#     controle.save()

#     estagiarios_processados_neste_ciclo.clear()
#     logger.info("🔄 Controle de logs resetado - cache limpo - próxima execução processará tudo como novo")
