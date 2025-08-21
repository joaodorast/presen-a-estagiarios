# filepath: core/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_time
from .models import Estagiario, Presenca, Area, Usuario
import json
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime, date

def usuario_logado_required(view_func):
    """Decorador para verificar se o usuário está logado usando o sistema customizado"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_logado'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Verificar usando o modelo Usuario customizado
        try:
            usuario = Usuario.objects.get(login=username, senha=password)
            # Armazenar informações do usuário na sessão
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nome'] = usuario.nome
            request.session['usuario_area'] = usuario.area
            request.session['usuario_unidade'] = usuario.unidade
            request.session['usuario_logado'] = True
            
            print(f"Login realizado com sucesso: {usuario.nome}")
            return redirect('index')  # Redireciona para a página inicial
        except Usuario.DoesNotExist:
            print(f"Tentativa de login falhada para: {username}")
            return render(request, 'login.html', {'error': 'Usuário ou senha inválidos'})
    
    return render(request, 'login.html')

def logout_view(request):
    # Limpar dados da sessão do usuário customizado
    request.session.flush()  # Remove todas as variáveis da sessão
    return redirect('login')

def index(request):
    if not request.session.get('usuario_logado'):
        return redirect('login')  # Redireciona para a página de login se não estiver autenticado
    
    # Passar dados do usuário para o template
    context = {
        'usuario_nome': request.session.get('usuario_nome'),
        'usuario_area': request.session.get('usuario_area'),
        'usuario_unidade': request.session.get('usuario_unidade')
    }
    return render(request, 'index.html', context)

def get_area(id):
    try:
        area = Area.objects.get(id=id)
        return area
    except Area.DoesNotExist:
        return None

@csrf_exempt
def get_estagiarios(request):
    if request.method == 'GET':
        # Verificar se o usuário está logado
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        # Obter a unidade do usuário logado
        unidade_usuario = request.session.get('usuario_unidade')
        print(f"Unidade do usuário logado: {unidade_usuario}")
        
        if not unidade_usuario:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)
        
        # Filtrar estagiários apenas da mesma unidade
        print(Estagiario.objects.filter(unidade = "Campos Eliseos"))
        estagiarios = list(Estagiario.objects.filter(unidade=unidade_usuario).values())
        
        
        for estagiario in estagiarios:
            area = get_area(estagiario['area_id'])
            estagiario['area'] = area.nome if area else 'Área não encontrada'
            estagiario['temControlId'] = bool(estagiario.get('control_id_user_id'))
            print(f"Estagiário {estagiario['nome']} da unidade {estagiario['unidade']}")
        
        return JsonResponse({
            'estagiarios': estagiarios, 
            'unidade_filtro': unidade_usuario,
            'total': len(estagiarios)
        }, safe=False)
    
def total_estagiarios_area(area_id, unidade=None):
    """Conta estagiários por área, opcionalmente filtrados por unidade"""
    if unidade:
        return Estagiario.objects.filter(area_id=area_id, unidade=unidade).count()
    return Estagiario.objects.filter(area_id=area_id).count()
    
@csrf_exempt
def get_areas(request):
    if request.method == 'GET':
        # Verificar se o usuário está logado
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        # Obter a unidade do usuário logado
        unidade_usuario = request.session.get('usuario_unidade')
        
        if not unidade_usuario:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)
        
        # Filtrar áreas apenas da mesma unidade
        areas = list(Area.objects.filter(unidade=unidade_usuario).values())
        
        for area in areas:
            # Contar estagiários da área na mesma unidade
            area['total_estagiarios'] = total_estagiarios_area(area['id'], unidade_usuario)
        
        return JsonResponse({
            'areas': areas, 
            'unidade_filtro': unidade_usuario,
            'total': len(areas)
        }, safe=False)
    

@csrf_exempt
def create_area(request):
    if request.method == 'POST':
        # Verificar se o usuário está logado
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        # Obter a unidade do usuário logado
        unidade_usuario = request.session.get('usuario_unidade')
        
        if not unidade_usuario:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)
        
        # Criar uma nova área
        data = json.loads(request.body)
        area = Area.objects.create(
            nome=data['nome'],
            unidade=unidade_usuario,  # Automaticamente define a unidade do usuário
            descricao=data.get('descricao', '')
        )
        return JsonResponse({
            'id': area.id, 
            'message': f'Área criada na unidade {unidade_usuario}'
        }, status=201)

    elif request.method == 'PUT':
        # Verificar se o usuário está logado
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        unidade_usuario = request.session.get('usuario_unidade')
        
        # Editar uma área existente
        data = json.loads(request.body)
        try:
            # Só permite editar áreas da mesma unidade
            area = Area.objects.get(id=data['id'], unidade=unidade_usuario)
            area.nome = data['nome']
            area.descricao = data.get('descricao', '')
            area.save()
            return JsonResponse({'message': 'Área atualizada com sucesso!'}, status=200)
        except Area.DoesNotExist:
            return JsonResponse({'error': 'Área não encontrada ou sem permissão'}, status=404)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def delete_area(request, area_id):
    if request.method == 'DELETE':
        # Verificar se o usuário está logado
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        unidade_usuario = request.session.get('usuario_unidade')
        
        try:
            # Só permite deletar áreas da mesma unidade
            area = Area.objects.get(id=area_id, unidade=unidade_usuario)
            area.delete()
            return JsonResponse({'message': 'Área deletada com sucesso!'}, status=200)
        except Area.DoesNotExist:
            return JsonResponse({'error': 'Área não encontrada ou sem permissão'}, status=404)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)


@csrf_exempt
def create_estagiario(request):
    if request.method == 'POST':
        # Verificar se o usuário está logado
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        unidade_usuario = request.session.get('usuario_unidade')
        
        if not unidade_usuario:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)
        
        # Criar um novo estagiário
        data = json.loads(request.body)
        
        # Verificar se a área pertence à mesma unidade
        try:
            area = Area.objects.get(id=data['area'], unidade=unidade_usuario)
        except Area.DoesNotExist:
            return JsonResponse({'error': 'Área não encontrada ou sem permissão'}, status=404)
        
        estagiario = Estagiario.objects.create(
            nome=data['nome'],
            email=data['email'],
            unidade=unidade_usuario,  # Automaticamente define a unidade do usuário
            telefone=data['telefone'],
            data_inicio=data['dataInicio'],
            area=area,  
            ativo=data['ativo']
        )
        return JsonResponse({
            'id': estagiario.id, 
            'message': f'Estagiário criado na unidade {unidade_usuario}'
        }, status=201)

    elif request.method == 'PUT':
        # Verificar se o usuário está logado
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        unidade_usuario = request.session.get('usuario_unidade')
        
        # Editar um estagiário existente
        data = json.loads(request.body)
        try:
            # Só permite editar estagiários da mesma unidade
            estagiario = Estagiario.objects.get(id=data['id'], unidade=unidade_usuario)
            
            # Verificar se a nova área pertence à mesma unidade
            area = Area.objects.get(id=data['area'], unidade=unidade_usuario)
            
            estagiario.nome = data['nome']
            estagiario.email = data['email']
            estagiario.telefone = data['telefone']
            estagiario.data_inicio = data['dataInicio']
            estagiario.area = area
            estagiario.ativo = data['ativo']
            estagiario.save()
            return JsonResponse({'message': 'Estagiário atualizado com sucesso!'}, status=200)
        except (Estagiario.DoesNotExist, Area.DoesNotExist):
            return JsonResponse({'error': 'Estagiário ou área não encontrados ou sem permissão'}, status=404)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def delete_estagiario(request, estagiario_id):
    if request.method == 'DELETE':
        # Verificar se o usuário está logado
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        unidade_usuario = request.session.get('usuario_unidade')
        
        try:
            # Só permite deletar estagiários da mesma unidade
            estagiario = Estagiario.objects.get(id=estagiario_id, unidade=unidade_usuario)
            estagiario.delete()
            return JsonResponse({'message': 'Estagiário deletado com sucesso!'}, status=200)
        except Estagiario.DoesNotExist:
            return JsonResponse({'error': 'Estagiário não encontrado ou sem permissão'}, status=404)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def get_presencas(request):
    if request.method == 'GET':
        # Verificar se o usuário está logado
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        unidade_usuario = request.session.get('usuario_unidade')
        
        if not unidade_usuario:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)
        
        # Filtrar presenças apenas de estagiários da mesma unidade
        presencas = list(Presenca.objects.filter(
            estagiario__unidade=unidade_usuario
        ).values(
            'id', 'estagiario_id', 'data', 'entrada', 'saida', 'horas', 'observacao',
            'estagiario__nome', 'estagiario__unidade'  # Inclui nome e unidade do estagiário
        ))
        
        print(f"Presenças filtradas para unidade {unidade_usuario}: {len(presencas)}")
        return JsonResponse({
            'presencas': presencas, 
            'unidade_filtro': unidade_usuario,
            'total': len(presencas)
        }, safe=False)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def registrar_saida(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            presenca = Presenca.objects.get(id=data['presencaId'])
            presenca.saida = parse_time(data['saida'])
            presenca.horas = data['horas']
            presenca.observacao = data.get('observacao', '')
            presenca.save()
            return JsonResponse({'message': 'Saída registrada com sucesso!'}, status=200)
        except Presenca.DoesNotExist:
            return JsonResponse({'error': 'Presença não encontrada'}, status=404)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def registrar_entrada(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        estagiario = Estagiario.objects.get(id=data['estagiarioId'])
        entrada = parse_time(data['entrada'])
        presenca = Presenca.objects.create(estagiario=estagiario, data=data['data'], entrada=entrada)
        return JsonResponse({'message': 'Entrada registrada com sucesso!', 'id': presenca.id}, status=201)

#  adiconei uma nova view: 
def calculadora_horas(request):
    if not request.session.get('usuario_logado'):
        return redirect('login')
    return render(request, 'calculadora-hour.html')

@csrf_exempt
def criar_usuario_admin(request):
    """Função para criar usuário administrador inicial - usar apenas uma vez"""
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            usuario = Usuario.objects.create(
                nome=data['nome'],
                area=data['area'],
                unidade=data['unidade'],
                login=data['login'],
                senha=data['senha']  # Em produção, use hash da senha
            )
            return JsonResponse({
                'message': 'Usuário criado com sucesso!',
                'id': usuario.id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def get_usuarios(request):
    """Listar usuários (apenas para admins)"""
    if request.method == 'GET':
        usuarios = list(Usuario.objects.values('id', 'nome', 'area', 'unidade', 'login'))
        return JsonResponse({'usuarios': usuarios}, safe=False)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def alterar_senha(request):
    """Alterar senha do usuário logado"""
    if not request.session.get('usuario_logado'):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        usuario_id = request.session.get('usuario_id')
        
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            # Verificar senha atual
            if usuario.senha != data['senha_atual']:
                return JsonResponse({'error': 'Senha atual incorreta'}, status=400)
            
            # Atualizar senha
            usuario.senha = data['nova_senha']
            usuario.save()
            
            return JsonResponse({'message': 'Senha alterada com sucesso!'}, status=200)
        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Usuário não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)  

@csrf_exempt
def receber_evento(request):
    """
    Endpoint para receber eventos do Control ID
    O Control ID pode enviar dados via GET (parâmetros na URL) ou POST (no body)
    """
    print(f"Método: {request.method}")
    print(f"Body: {request.body}")
    print(f"GET params: {request.GET}")
    print(f"Headers: {dict(request.headers)}")
    
    if request.method == 'GET':
        # Control ID enviando parâmetros via GET
        device_id = request.GET.get('deviceId')
        uuid = request.GET.get('uuid')
        user_id = request.GET.get('user_id')
        event = request.GET.get('event')
        
        print(f"Parâmetros GET - deviceId: {device_id}, uuid: {uuid}, user_id: {user_id}, event: {event}")
        
        # Se não tem dados específicos, é apenas um ping/heartbeat
        if not user_id and not event:
            return JsonResponse({
                'status': 'ok', 
                'message': 'Heartbeat recebido',
                'deviceId': device_id,
                'uuid': uuid
            }, status=200)
        
        # Se tem dados de evento, processar
        if user_id and event:
            dados = {
                'user_id': user_id,
                'event': event,
                'device_id': device_id,
                'uuid': uuid,
                'timestamp': datetime.now().isoformat(),
                'method': 'GET'
            }
            
            # Aqui você pode processar o evento
            print(f"Evento processado: {dados}")
            
            return JsonResponse({
                'status': 'ok',
                'message': 'Evento processado com sucesso',
                'data': dados
            }, status=200)
        
        # Resposta padrão para GET
        return JsonResponse({
            'status': 'ok',
            'message': 'GET recebido',
            'deviceId': device_id,
            'uuid': uuid
        }, status=200)
    
    elif request.method == 'POST':
        # Control ID enviando dados via POST
        try:
            if request.body:
                dados = json.loads(request.body)
                print(f"Dados POST recebidos: {dados}")
                
                # Processar dados do POST
                return JsonResponse({
                    'status': 'ok',
                    'message': 'Dados POST processados',
                    'data': dados
                }, status=200)
            else:
                # POST sem body
                return JsonResponse({
                    'status': 'ok',
                    'message': 'POST vazio recebido'
                }, status=200)
                
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return JsonResponse({
                'erro': 'JSON inválido',
                'body': request.body.decode('utf-8') if request.body else ''
            }, status=400)
        except Exception as e:
            print(f"Erro geral: {e}")
            return JsonResponse({'erro': str(e)}, status=400)
    
    return JsonResponse({
        'erro': f'Método {request.method} não suportado'
    }, status=405) 

import json
import re
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import PushCommand, ResultCommand

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

@csrf_exempt
def push(request):
    if request.method == 'GET':
        device_id = request.GET.get('deviceId')
        uuid = request.GET.get('uuid')

        if not device_id or not uuid:
            return JsonResponse({'error': 'Faltando parâmetros'}, status=400)

        # Você precisa definir a URL do dispositivo (IP fixo, hostname ou DNS)
        DEVICE_BASE_URL = f"http://192.168.1.93:8081"

        # Faz uma requisição para obter os dados do evento
        try:
            response = requests.get(f"{DEVICE_BASE_URL}/event?uuid={uuid}", timeout=5)
            if response.status_code != 200:
                print(f"Erro ao buscar evento: {response.status_code} - {response.text}")
                return JsonResponse({'error': 'Erro ao buscar evento no dispositivo'}, status=500)

            dados = response.json()

            # Exemplo de dados que podem vir do evento
            evento = {
                "usuario": dados.get("user", {}).get("name", "Desconhecido"),
                "uuid": uuid,
                "device_id": device_id,
                "tipo": dados.get("event", {}).get("type", "desconhecido"),
                "horario": dados.get("event", {}).get("timestamp", now().isoformat()),
            }

            # Aqui você pode salvar no seu modelo de logs
            print("Evento:", evento)

            # TODO: Salvar no banco de dados se quiser
            # LogDeAcesso.objects.create(...)

            return JsonResponse({"mensagem": "Evento registrado com sucesso", "dados": evento})

        except requests.RequestException as e:
            print(f"Erro ao conectar com o dispositivo: {e}")
            return JsonResponse({'error': 'Falha na conexão com o leitor'}, status=500)

    return JsonResponse({'error': 'Método não permitido'}, status=405)


@csrf_exempt
def result(request):
    if request.method == 'POST':
        device_id = request.GET.get('deviceId')
        uuid = request.GET.get('uuid')
        endpoint_param = request.GET.get('endpoint')

        if not device_id or not uuid:
            return JsonResponse({'erro': 'Parâmetros deviceId e uuid são obrigatórios.'}, status=400)

        try:
            body_str = request.body.decode('utf-8')
            # Corrige 'undefined' no JSON para null, se necessário
            body_str = re.sub(r'"endpoint"\s*:\s*undefined', '"endpoint": null', body_str)
            dados = json.loads(body_str) if body_str else {}
        except json.JSONDecodeError:
            return JsonResponse({'erro': 'Corpo da requisição não é um JSON válido.'}, status=400)

        # Se houver erro no payload, logue e responda OK para evitar retry
        if 'error' in dados:
            print(f"Erro recebido do dispositivo: {dados['error']}")
            return JsonResponse({'status': 'erro no payload do dispositivo'}, status=200)

        response_data = dados.get('response')
        error_data = dados.get('error')

        ResultCommand.objects.create(
            device_id=device_id,
            uuid=uuid,
            endpoint=endpoint_param,
            response=response_data,
            error=error_data
        )

        return JsonResponse({'status': 'ok'}, status=200)
    else:
        return JsonResponse({'erro': 'Método não permitido'}, status=405)