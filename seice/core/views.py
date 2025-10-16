# filepath: core/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_time, parse_datetime
from .models import Estagiario, Presenca, Area, Usuario, Unidade, UsuarioUnidade
import json
import requests
import logging
import threading
import time
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, timedelta

# Configurar logging
logger = logging.getLogger(__name__)

# Configurações do Control ID
CONTROL_ID_BASE_URL = "http://192.168.3.40"
CONTROL_ID_SESSION = ""  # Será preenchido dinamicamente

# Controle da coleta de logs
log_collector_active = False
log_collector_thread = None
log_collector_config = {
    'interval': 30,  # segundos entre coletas
    'control_id_ip': '192.168.3.40:81',
    'session': '',
    'last_collection': None,  # último timestamp de coleta
    'total_collected': 0  # total de logs coletados
}

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
            # Obter unidade do usuário
            usuario_unidade = UsuarioUnidade.objects.filter(usuario=usuario).first()
            if not usuario_unidade:
                print(f"Usuário {username} não tem unidade associada")
                return render(request, 'login.html', {'error': 'Usuário não tem unidade associada'})
            # Armazenar informações do usuário na sessão
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nome'] = usuario.nome
            request.session['usuario_area'] = usuario.area
            request.session['usuario_unidade'] = usuario_unidade.unidade.id
            request.session['usuario_logado'] = True

            print(f"Login realizado com sucesso: {usuario.nome}")
            return redirect('index')
        except Usuario.DoesNotExist:
            print(f"Tentativa de login falhada para: {username}")
            return render(request, 'login.html', {'error': 'Usuário ou senha inválidos'})

    return render(request, 'login.html')

@csrf_exempt
def login_control_id(request):
    if request.method == 'POST':
        user = "admin"
        password = "admin"
        base_url = "http://192.168.3.40:81/login.fcgi"
        facial_id_url = "http://192.168.3.40:81/login.fcgi"
        try:
            # Envia login e senha para o Facial ID
            resp = requests.post(
                facial_id_url,
                data={'login': user, 'password': password}
            )
            resp.raise_for_status()
            session_data = resp.json()
            # Salva o token de sessão na sessão do Django (opcional)
            request.session['facial_id_session'] = session_data.get('session')
            return JsonResponse({'status': 'ok', 'session': session_data.get('session')}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def logout_view(request):
    # Limpar dados da sessão do usuário customizado
    request.session.flush()  # Remove todas as variáveis da sessão
    return redirect('login')

def index(request):
    if not request.session.get('usuario_logado'):
        return redirect('login')

    unidades = UsuarioUnidade.objects.filter(
        usuario_id=request.session.get('usuario_id')
    ).select_related('unidade')

    context = {
        'area_usuario': request.session.get('usuario_area'),
        'nome_usuario': request.session.get('usuario_nome'),
        'unidades': unidades  # passa a lista inteira
    }

    return render(request, 'welcome.html', context)

def unit_panel(request, unit_id):
    if not request.session.get('usuario_logado'):
        return redirect('login')

    try:
        unidade = Unidade.objects.get(id=unit_id)
    except Unidade.DoesNotExist:
        return redirect('index')

# Atualizar unidade do usuário na sessão para filtrar dados
    request.session['usuario_unidade'] = unidade.id

    context = {
        'usuario_nome': request.session.get('usuario_nome'),
        'usuario_area': request.session.get('usuario_area'),
        'usuario_unidade': request.session.get('usuario_unidade'),
        'usuario_unidade_nome': unidade.nome
    }
    # Renderizar o template baseado na área do usuário
    area_usuario = request.session.get('usuario_area', '').lower()
    # template_name = f"{area_usuario}.html"
    template_name = 'tecnologia.html'
    return render(request, template_name, context)


def educacao_fisica(request):
    if not request.session.get('usuario_logado'):
        return redirect('login')
    context = {
        'usuario_nome': request.session.get('usuario_nome'),
        'usuario_area': request.session.get('usuario_area'),
        'usuario_unidade': request.session.get('usuario_unidade'),

    }
    return render(request, 'educacao-fisica.html', context)

def manutencao(request):
    if not request.session.get('usuario_logado'):
        return redirect('login')
    context = {
        'usuario_nome': request.session.get('usuario_nome'),
        'usuario_area': request.session.get('usuario_area'),
        'usuario_unidade': request.session.get('usuario_unidade'),

    }
    return render(request, 'manutencao.html', context)

def tecnologia(request):
    if not request.session.get('usuario_logado'):
        return redirect('login')
    context = {
        'usuario_nome': request.session.get('usuario_nome'),
        'usuario_area': request.session.get('usuario_area'),
        'usuario_unidade': request.session.get('usuario_unidade'),
    }
    return render(request, 'tecnologia.html', context)


def financeiro(request):
    if not request.session.get('usuario_logado'):
        return redirect('login')
    context = {
        'usuario_nome': request.session.get('usuario_nome'),
        'usuario_area': request.session.get('usuario_area'),
        'usuario_unidade': request.session.get('usuario_unidade')
    }
    return render(request, 'financeiro.html', context)

def pedagogia(request):
    if not request.session.get('usuario_logado'):
        return redirect('login')
    context = {
        'usuario_nome': request.session.get('usuario_nome'),
        'usuario_area': request.session.get('usuario_area'),
        'usuario_unidade': request.session.get('usuario_unidade'),

    }
    return render(request, 'pedagogia.html', context)

def coordenacao(request):
    if not request.session.get('usuario_logado'):
        return redirect('login')
    context = {
        'usuario_nome': request.session.get('usuario_nome'),
        'usuario_area': request.session.get('usuario_area'),
        'usuario_unidade': request.session.get('usuario_unidade'),

    }
    return render(request, 'pedagogia.html', context)



def get_area(id):
    try:
        area = Area.objects.get(id=id)
        return area
    except Area.DoesNotExist:
        return None


@csrf_exempt
def get_estagiarios(request):
    if request.method == 'GET':
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)

        unidade_id = request.session.get('usuario_unidade')
        usuario_area = str(request.session.get('usuario_area', '')).strip().lower()
        if not unidade_id:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)

        # RH pode ver todos os estagiários de todas as unidades e setores
        if usuario_area == 'rh' or usuario_area == 'recursos humanos':
            estagiarios_qs = Estagiario.objects.select_related("area", "unidade")
        else:
            estagiarios_qs = Estagiario.objects.filter(unidade_id=unidade_id, setor=usuario_area).select_related("area", "unidade")

        estagiarios = []
        for e in estagiarios_qs:
            estagiarios.append({
                "id": e.id,
                "nome": e.nome,
                "area_id": e.area.id if e.area else None,
                "area": e.area.nome if e.area else "Área não encontrada",
                "unidade": e.unidade.nome if e.unidade else "Unidade não encontrada",
                "setor": getattr(e, 'setor', ''),
                "email": e.email,
                "data_inicio": e.data_inicio,
                "ativo": e.ativo,
                "control_id_user_id": e.control_id_user_id,
                "temControlId": bool(e.control_id_user_id),
            })

        return JsonResponse({
            'estagiarios': estagiarios,
            'unidade_filtro': unidade_id,
            'total': len(estagiarios)
        })


def total_estagiarios_area(area_id, unidade_id=None):
    """Conta estagiários por área, opcionalmente filtrados por unidade"""
    qs = Estagiario.objects.filter(area_id=area_id)
    if unidade_id:
        qs = qs.filter(unidade_id=unidade_id)
    return qs.count()


@csrf_exempt
def get_areas(request):
    if request.method == 'GET':
        if not request.session.get('usuario_logado'):
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)

        unidade_id = request.session.get('usuario_unidade')
        usuario_area = str(request.session.get('usuario_area', '')).strip().lower()
        if not unidade_id:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)

        # RH pode ver todas as áreas de todas as unidades e setores
        if usuario_area == 'rh' or usuario_area == 'recursos humanos':
            areas_qs = Area.objects.select_related('unidade')
        else:
            areas_qs = Area.objects.filter(unidade_id=unidade_id, setor=usuario_area).select_related('unidade')

        areas = []
        for a in areas_qs:
            areas.append({
                "id": a.id,
                "nome": a.nome,
                "unidade": a.unidade.nome if a.unidade else "Unidade não encontrada",
                "setor": getattr(a, 'setor', ''),
                "total_estagiarios": total_estagiarios_area(a.id, unidade_id)
            })

        return JsonResponse({
            'areas': areas,
            'unidade_filtro': unidade_id,
            'total': len(areas)
        })

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
        try:
            unidade = Unidade.objects.get(id=unidade_usuario)
        except Unidade.DoesNotExist:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)

        area = Area.objects.create(
            nome=data['nome'],
            unidade=unidade, 
            setor = request.session.get('usuario_area'),
             # Passa a instância da Unidade
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

        if not unidade_usuario:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)

        # Editar uma área existente
        data = json.loads(request.body)
        try:
            unidade = Unidade.objects.get(id=unidade_usuario)
        except Unidade.DoesNotExist:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)

        try:
            # Só permite editar áreas da mesma unidade
            area = Area.objects.get(id=data['id'], unidade=unidade)
            area.nome = data['nome']
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

        try:
            unidade = Unidade.objects.get(id=unidade_usuario)
        except Unidade.DoesNotExist:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)

        estagiario = Estagiario.objects.create(
            nome=data['nome'],
            email=data['email'],
            unidade=unidade,  # Passa a instância da Unidade
            data_inicio=data['dataInicio'],
            setor = request.session.get('usuario_area'),    
            area=area,
            ativo=data['ativo'],
            control_id_user_id=data.get('control_id_user_id', '')  # <-- Adicionado
        )
        return JsonResponse({
            'id': estagiario.id, 
            'message': f'Estagiário criado na unidade {unidade_usuario}'
        }, status=201)

    elif request.method == 'PUT':
        print(json.loads(request.body))
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
            estagiario.data_inicio = data['dataInicio']
            area = Area.objects.get(id=data['area'], unidade=unidade_usuario)
            estagiario.ativo = data['ativo']
            estagiario.control_id_user_id = data.get('control_id_user_id', '')

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
        usuario_area = str(request.session.get('usuario_area', '')).strip().lower()
        if not unidade_usuario:
            return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)

        # RH pode ver todas as presenças de todos os setores
        if usuario_area == 'rh' or usuario_area == 'recursos humanos':
            presencas = list(Presenca.objects.filter(
                estagiario__ativo=True
            ).values(
                'id', 'estagiario_id', 'data', 'entrada', 'saida', 'horas', 'observacao',
                'estagiario__nome', 'estagiario__unidade', 'estagiario__setor'
            ))
        else:
            presencas = list(Presenca.objects.filter(
                estagiario__unidade=unidade_usuario, estagiario__setor=usuario_area, estagiario__ativo=True
            ).values(
                'id', 'estagiario_id', 'data', 'entrada', 'saida', 'horas', 'observacao',
                'estagiario__nome', 'estagiario__unidade', 'estagiario__setor'
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
def adicionar_control_id_estagiario(request):
    """Adicionar ID do Control ID a um estagiário"""
    if not request.session.get('usuario_logado'):
        return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            unidade_usuario = request.session.get('usuario_unidade')
            
            if not unidade_usuario:
                return JsonResponse({'error': 'Unidade do usuário não encontrada'}, status=400)
            
            # Só permite editar estagiários da mesma unidade
            estagiario = Estagiario.objects.get(
                id=data['estagiarioId'], 
                unidade=unidade_usuario
            )
            estagiario.control_id_user_id = data['controlIdUserId']
            estagiario.save()
            
            return JsonResponse({
                'message': f'ID do Control ID ({data["controlIdUserId"]}) adicionado ao estagiário {estagiario.nome} com sucesso!'
            }, status=200)
        except Estagiario.DoesNotExist:
            return JsonResponse({'error': 'Estagiário não encontrado ou sem permissão'}, status=404)
        except KeyError as e:
            return JsonResponse({'error': f'Campo obrigatório faltando: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == 'GET':
        # Retornar informações sobre como usar a API
        return JsonResponse({
            'message': 'Endpoint para adicionar ID do Control ID ao estagiário',
            'usage': {
                'method': 'POST',
                'body': {
                    'estagiarioId': 'ID do estagiário',
                    'controlIdUserId': 'ID do usuário no Control ID'
                }
            }
        })
    
    return JsonResponse({'error': 'Método não permitido. Use POST para adicionar ID do Control ID.'}, status=405)  


@csrf_exempt
def editar_presenca(request, presenca_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            presenca = Presenca.objects.get(id=presenca_id)
            if data.get('entrada'):
                presenca.entrada = parse_time(data['entrada'])
            if data.get('saida'):
                presenca.saida = parse_time(data['saida'])
            if data.get('horas'):
                presenca.horas = data['horas']
            presenca.observacao = data.get('observacao', '')
            presenca.save()
            return JsonResponse({'message': 'Presença editada com sucesso!'}, status=200)
        except Presenca.DoesNotExist:
            return JsonResponse({'error': 'Presença não encontrada'}, status=404)
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def deletar_presenca(request, presenca_id):
    if request.method == 'DELETE':
        try:
            presenca = Presenca.objects.get(id=presenca_id)
            presenca.delete()
            return JsonResponse({'message': 'Presença excluída com sucesso!'}, status=200)
        except Presenca.DoesNotExist:
            return JsonResponse({'error': 'Presença não encontrada'}, status=404)
    return JsonResponse({'error': 'Método não permitido'}, status=405)



# @csrf_exempt
# def carregar_objetos_controlid(request):
#     if request.method == 'GET':
#         # Chama a função que faz login no Facial ID e retorna o token de sessão
#         resp = login_control_id(request)
#         # Se login_control_id retorna um JsonResponse, extraia o token
#         if isinstance(resp, JsonResponse):
#             session_data = resp.content.decode()
#             try:
#                 import json
#                 session = json.loads(session_data).get('session')
#             except Exception:
#                 return JsonResponse({'erro': 'Falha ao obter sessão do Facial ID.'}, status=500)
#         elif isinstance(resp, dict):
#             session = resp.get('session')
#         else:
#             session = "cTwub3uGBhYwcmuaRyfWxIhZ"

#         if not session:
#             return JsonResponse({'erro': 'Não foi possível obter o token de sessão.'}, status=400)

#         url = f"http://192.168.3.40:81/load_objects.fcgi?session={session}"
#         try:
#             response = requests.get(url, timeout=10)
#             response.raise_for_status()
#             dados = response.json()
            
#             # Processar logs automaticamente se existirem
#             if 'access_logs' in dados:
#                 logs_processados = processar_logs_control_id(dados, request.session.get('usuario_unidade'))
#                 dados['logs_processados'] = logs_processados['processados']
#                 dados['logs_ignorados'] = logs_processados['ignorados']
                
#             return JsonResponse({'dados': dados}, status=200)
#         except Exception as e:
#             return JsonResponse({'erro': str(e)}, status=500)
#     return JsonResponse({'erro': 'Método não permitido'}, status=405)

# @csrf_exempt
# def processar_logs_control_id(logs_data, unidade_usuario):
#     """
#     Processa os logs recebidos do Control ID e cria presenças automaticamente
#     """
#     processados = 0
#     ignorados = 0
    
#     if not unidade_usuario:
#         return {'processados': 0, 'ignorados': 0}
    
#     try:
#         access_logs = logs_data.get('access_logs', [])
#         for log in access_logs:
#             try:
#                 user_id = str(log.get('user_id', ''))
#                 timestamp = log.get('time')
#                 event_type = str(log.get('event', 'unknown')).lower()
#                 log_unique_id = f"{user_id}-{timestamp}-{event_type}"
#                 # Verificação extra: não processar se já existe presença com esse log
#                 if not user_id or not timestamp:
#                     ignorados += 1
#                     continue
#                 # Converter timestamp
#                 if isinstance(timestamp, str):
#                     log_datetime = parse_datetime(timestamp)
#                     if not log_datetime:
#                         try:
#                             log_datetime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
#                         except:
#                             try:
#                                 log_datetime = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
#                             except:
#                                 ignorados += 1
#                                 continue
#                 elif isinstance(timestamp, (int, float)):
#                     log_datetime = datetime.fromtimestamp(timestamp)
#                 else:
#                     ignorados += 1
#                     continue
#                 try:
#                     estagiario = Estagiario.objects.get(
#                         control_id_user_id=user_id,
#                         unidade=unidade_usuario,
#                         ativo=True
#                     )
#                 except Estagiario.DoesNotExist:
#                     ignorados += 1
#                     continue
#                 data_log = log_datetime.date()
#                 hora_log = log_datetime.time()
#                 # DUPLICIDADE: Verificar se já existe presença com esse log
#                 if Presenca.objects.filter(
#                     estagiario=estagiario,
#                     data=data_log,
#                     entrada=hora_log
#                 ).exists():
#                     ignorados += 1
#                     continue
#                 # Processar entrada
#                 if event_type in ['in', 'entrada', 'face_in', 'entry', '1']:
#                     presenca_existente = Presenca.objects.filter(
#                         estagiario=estagiario,
#                         data=data_log
#                     ).first()
#                     if not presenca_existente:
#                         Presenca.objects.create(
#                             estagiario=estagiario,
#                             data=data_log,
#                             entrada=hora_log,
#                             observacao=f'Entrada automática via Control ID - Log {log.get("id", "N/A")}'
#                         )
#                         processados += 1
#                         logger.info(f"Presença criada para {estagiario.nome} em {data_log} às {hora_log}")
#                     else:
#                         if hora_log < presenca_existente.entrada:
#                             presenca_existente.entrada = hora_log
#                             presenca_existente.observacao += f' | Entrada atualizada via Control ID'
#                             presenca_existente.save()
#                             processados += 1
#                             logger.info(f"Entrada atualizada para {estagiario.nome} em {data_log}")
#                         else:
#                             ignorados += 1
#                 elif event_type in ['out', 'saida', 'face_out', 'exit', '0']:
#                     presenca = Presenca.objects.filter(
#                         estagiario=estagiario,
#                         data=data_log,
#                         saida__isnull=True
#                     ).first()
#                     if presenca:
#                         # Se a saída for no mesmo horário da entrada, ignora
#                         if hora_log == presenca.entrada:
#                             logger.info(f"Saída ignorada para {estagiario.nome} em {data_log} pois horário é igual à entrada ({hora_log})")
#                             ignorados += 1
#                             continue
#                         presenca.saida = hora_log
#                         entrada_datetime = datetime.combine(data_log, presenca.entrada)
#                         saida_datetime = datetime.combine(data_log, hora_log)
#                         horas_trabalhadas = saida_datetime - entrada_datetime
#                         total_seconds = int(horas_trabalhadas.total_seconds())
#                         hours = total_seconds // 3600
#                         minutes = (total_seconds % 3600) // 60
#                         presenca.horas = f"{hours:02d}:{minutes:02d}"
#                         if presenca.observacao:
#                             presenca.observacao += f' | Saída automática via Control ID'
#                         else:
#                             presenca.observacao = f'Saída automática via Control ID'
#                         presenca.save()
#                         processados += 1
#                         logger.info(f"Saída registrada para {estagiario.nome} em {data_log} às {hora_log}")
#                     else:
#                         ignorados += 1
#                 else:
#                     ignorados += 1
#             except Exception as e:
#                 logger.error(f"Erro ao processar log individual: {str(e)}")
#                 ignorados += 1
#                 continue
#     except Exception as e:
#         logger.error(f"Erro geral no processamento de logs: {str(e)}")
#     logger.info(f"Processamento concluído: {processados} processados, {ignorados} ignorados")
#     return {
#         'processados': processados,
#         'ignorados': ignorados
#     }

# @csrf_exempt
# def coletar_logs_control_id():
#     """
#     Função que roda em background para coletar logs do Control ID periodicamente
#     """
#     global log_collector_active
    
#     while log_collector_active:
#         try:
#             logger.info("Iniciando coleta de logs do Control ID...")
            
#             # Fazer login no Control ID para obter sessão
#             session_id = obter_sessao_control_id()
#             if not session_id:
#                 logger.error("Não foi possível obter sessão do Control ID")
#                 time.sleep(log_collector_config['interval'])
#                 continue
            
#             # Buscar logs do Control ID
#             url = f"http://{log_collector_config['control_id_ip']}/load_objects.fcgi"
#             params = {'session': session_id}
#             headers = {'Content-Type': 'application/json'}
#             payload = {"object": "access_logs"}
            
#             response = requests.post(
#                 url,
#                 params=params,
#                 headers=headers,
#                 json=payload,
#                 timeout=30
#             )
            
#             if response.status_code == 200:
#                 logs_data = response.json()
                
#                 # Salvar logs coletados
#                 if 'access_logs' in logs_data:
#                     logs_coletados = logs_data['access_logs']
#                     log_collector_config['total_collected'] += len(logs_coletados)
#                     log_collector_config['last_collection'] = datetime.now().isoformat()
                    
#                     logger.info(f"Coletados {len(logs_coletados)} logs do Control ID")
                    
#                     # Aqui você pode processar ou salvar os logs como quiser
#                     # Por exemplo, salvar em arquivo ou processar diretamente
#                     print(f"=== LOGS COLETADOS ({len(logs_coletados)}) ===")
#                     for log in logs_coletados[:5]:  # Mostrar apenas os 5 primeiros
#                         print(f"User ID: {log.get('user_id')}, Time: {log.get('time')}, Event: {log.get('event')}")
#                     if len(logs_coletados) > 5:
#                         print(f"... e mais {len(logs_coletados) - 5} logs")
#                     print("=== FIM DOS LOGS ===")
#                 else:
#                     logger.info("Nenhum log encontrado na resposta")
#             else:
#                 logger.error(f"Erro na coleta de logs: {response.status_code} - {response.text}")
        
#         except Exception as e:
#             logger.error(f"Erro na coleta de logs: {str(e)}")
        
#         # Aguardar o intervalo configurado
#         time.sleep(log_collector_config['interval'])

# @csrf_exempt
# def obter_sessao_control_id():
#     """
#     Faz login no Control ID e retorna o session ID
#     """
#     try:
#         url = "http://192.168.3.40:81/login.fcgi"
#         response = requests.post(
#             url,
#             data={'login': 'admin', 'password': 'admin'},
#             timeout=10
#         )
        
#         if response.status_code == 200:
#             session_data = response.json()
#             return session_data.get('session')
#         else:
#             logger.error(f"Erro no login Control ID: {response.status_code}")
#             return None
#     except Exception as e:
#         logger.error(f"Erro ao fazer login no Control ID: {str(e)}")
#         return None


# @csrf_exempt
# def controlar_coleta_logs(request):
#     """
#     Controla a coleta periódica de logs do Control ID
#     """
#     global log_collector_active, log_collector_thread
    
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             action = data.get('action')
            
#             if action == 'start':
#                 if log_collector_active:
#                     return JsonResponse({'message': 'Coleta de logs já está ativa'}, status=200)
                
#                 # Configurar parâmetros
#                 log_collector_config['interval'] = data.get('interval', 30)
#                 log_collector_config['control_id_ip'] = data.get('control_id_ip', '192.168.3.40:81')
                
#                 # Iniciar thread
#                 log_collector_active = True
#                 log_collector_thread = threading.Thread(target=coletar_logs_control_id, daemon=True)
#                 log_collector_thread.start()
                
#                 logger.info(f"Coleta de logs iniciada - Intervalo: {log_collector_config['interval']}s")
#                 return JsonResponse({
#                     'message': 'Coleta de logs iniciada',
#                     'config': log_collector_config
#                 }, status=200)
            
#             elif action == 'stop':
#                 if not log_collector_active:
#                     return JsonResponse({'message': 'Coleta de logs não está ativa'}, status=200)
                
#                 log_collector_active = False
#                 logger.info("Coleta de logs parada")
#                 return JsonResponse({'message': 'Coleta de logs parada'}, status=200)
            
#             elif action == 'status':
#                 return JsonResponse({
#                     'active': log_collector_active,
#                     'config': log_collector_config,
#                     'thread_alive': log_collector_thread.is_alive() if log_collector_thread else False
#                 }, status=200)
            
#             else:
#                 return JsonResponse({'error': 'Ação inválida. Use: start, stop ou status'}, status=400)
        
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
    
#     elif request.method == 'GET':
#         # Retornar status atual
#         return JsonResponse({
#             'active': log_collector_active,
#             'config': log_collector_config,
#             'thread_alive': log_collector_thread.is_alive() if log_collector_thread else False,
#             'usage': {
#                 'start': {
#                     'action': 'start',
#                     'interval': 30,
#                     'control_id_ip': '192.168.3.40:81'
#                 },
#                 'stop': {'action': 'stop'},
#                 'status': {'action': 'status'}
#             }
#         })
    
#     return JsonResponse({'error': 'Método não permitido'}, status=405)


# @csrf_exempt
# def coletar_logs_manual(request):
#     """
#     Executa uma coleta manual imediata dos logs
#     """
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body) if request.body else {}
#             control_id_ip = data.get('control_id_ip', '192.168.3.40:81')
            
#             # Obter sessão
#             session_id = obter_sessao_control_id()
#             if not session_id:
#                 return JsonResponse({'error': 'Não foi possível obter sessão do Control ID'}, status=500)
            
#             # Fazer requisição aos logs
#             url = f"http://{control_id_ip}/load_objects.fcgi"
#             params = {'session': session_id}
#             headers = {'Content-Type': 'application/json'}
#             payload = {"object": "access_logs"}
            
#             response = requests.post(
#                 url,
#                 params=params,
#                 headers=headers,
#                 json=payload,
#                 timeout=30
#             )
            
#             if response.status_code == 200:
#                 logs_data = response.json()
                
#                 if 'access_logs' in logs_data:
#                     logs = logs_data['access_logs']
#                     return JsonResponse({
#                         'success': True,
#                         'message': 'Logs coletados com sucesso',
#                         'total_logs': len(logs),
#                         'logs': logs,
#                         'timestamp': datetime.now().isoformat()
#                     }, status=200)
#                 else:
#                     return JsonResponse({
#                         'success': True,
#                         'message': 'Nenhum log encontrado',
#                         'total_logs': 0,
#                         'logs': [],
#                         'timestamp': datetime.now().isoformat()
#                     }, status=200)
#             else:
#                 return JsonResponse({
#                     'error': f'Erro na API Control ID: {response.status_code}',
#                     'details': response.text
#                 }, status=response.status_code)
        
#         except Exception as e:
#             return JsonResponse({
#                 'error': 'Erro na coleta manual de logs',
#                 'details': str(e)
#             }, status=500)
    
#     return JsonResponse({'error': 'Método não permitido'}, status=405)


# def iniciar_coleta_automatica_startup():
#     """
#     Inicia a coleta automática de logs do Control ID durante o startup do Django
#     """
#     global log_collector_active, log_collector_thread
    
#     try:
#         # Verificar se já está ativa
#         if log_collector_active and log_collector_thread and log_collector_thread.is_alive():
#             logger.info("🔄 Coleta automática já está ativa - ignorando startup")
#             return
        
#         # Configurar parâmetros padrão
#         log_collector_config['interval'] = 30  # A cada 30 segundos
#         log_collector_config['control_id_ip'] = '192.168.3.40:81'
#         log_collector_config['session'] = ''
        
#         # Iniciar thread de coleta
#         log_collector_active = True
#         log_collector_thread = threading.Thread(target=coletar_logs_control_id, daemon=True)
#         log_collector_thread.start()
        
#         logger.info(f"🚀 STARTUP: Coleta automática de logs iniciada!")
#         logger.info(f"   ⏱️ Intervalo: {log_collector_config['interval']}s")
#         logger.info(f"   🌐 IP Control ID: {log_collector_config['control_id_ip']}")
        
#         # Aguardar um pouco para verificar se a thread iniciou corretamente
#         time.sleep(1)
#         if log_collector_thread.is_alive():
#             logger.info("✅ Thread de coleta iniciada com sucesso!")
#         else:
#             logger.error("❌ Falha ao iniciar thread de coleta")
    
#     except Exception as e:
#         logger.error(f"❌ Erro ao iniciar coleta automática no startup: {str(e)}")


# def parar_coleta_automatica_shutdown():
#     """
#     Para a coleta automática durante o shutdown do Django
#     """
#     global log_collector_active
    
#     try:
#         if log_collector_active:
#             log_collector_active = False
#             logger.info("🛑 SHUTDOWN: Coleta automática de logs parada")
#         else:
#             logger.info("🔄 SHUTDOWN: Coleta automática já estava parada")
#     except Exception as e:
#         logger.error(f"❌ Erro ao parar coleta durante shutdown: {str(e)}")


# # ========================================
# # SISTEMA SIMPLES DE COLETA DE PRESENÇAS
# # ========================================

# @csrf_exempt
# def presencas_automaticas_status(request):
#     """Status do sistema SIMPLES de presenças automáticas"""
#     from .coleta_simples import status_coleta
    
#     if request.method == 'GET':
#         status = status_coleta()
#         return JsonResponse({
#             'sistema': 'Presenças Automáticas SIMPLES v2.0',
#             'status': status,
#             'mensagem': 'Processa apenas LOGS NOVOS e registra presenças automaticamente',
#             'recursos': [
#                 'Detecta logs novos automaticamente',
#                 'Identifica entrada/saída corretamente', 
#                 'Calcula horas trabalhadas',
#                 'Evita reprocessamento'
#             ]
#         })
    
#     return JsonResponse({'error': 'Método não permitido'}, status=405)

# @csrf_exempt
# def presencas_automaticas_manual(request):
#     """Executa coleta manual SIMPLES"""
#     from .coleta_simples import registrar_presencas_dos_logs
    
#     if request.method == 'POST':
#         try:
#             registrar_presencas_dos_logs()
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Coleta manual executada com sucesso!'
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'error': str(e)
#             }, status=500)
    
#     return JsonResponse({'error': 'Use POST'}, status=405)

# @csrf_exempt
# def presencas_automaticas_controle(request):
#     """Controla o sistema SIMPLES (start/stop/reset)"""
#     from .coleta_simples import iniciar_coleta_automatica, parar_coleta_automatica, resetar_controle_logs
    
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             action = data.get('action')
            
#             if action == 'start':
#                 iniciar_coleta_automatica()
#                 return JsonResponse({'message': 'Sistema iniciado!'})
#             elif action == 'stop':
#                 parar_coleta_automatica()
#                 return JsonResponse({'message': 'Sistema parado!'})
#             elif action == 'reset':
#                 resetar_controle_logs()
#                 return JsonResponse({'message': 'Controle de logs resetado!'})
#             else:
#                 return JsonResponse({'error': 'Use action: start, stop ou reset'}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
    
#     return JsonResponse({'error': 'Use POST'}, status=405)