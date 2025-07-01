# filepath: core/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_time
from .models import Estagiario, Presenca, Area
import json
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Credenciais para cada unidade
UNIT_CREDENTIALS = {
    'campos-elisios': {
        'username': 'seice2025',
        'password': 'seice@2025@',
        'redirect_page': '/index/'
    },
    'jardim-primavera': {
        'username': 'seicejp2025',
        'password': 'seicejp@2025@',
        'redirect_page': '/index-jardim-primavera/'
    }
}

def welcome_view(request):
    """Página de boas-vindas com seleção de unidades"""
    return render(request, 'welcome.html')

@csrf_exempt
def unit_login(request):
    """Endpoint para login específico por unidade"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            unit = data.get('unit')
            username = data.get('username')
            password = data.get('password')
            
            # Verificar se a unidade existe
            if unit not in UNIT_CREDENTIALS:
                return JsonResponse({
                    'success': False, 
                    'error': 'Unidade não encontrada'
                }, status=400)
            
            # Verificar credenciais da unidade
            unit_creds = UNIT_CREDENTIALS[unit]
            if username == unit_creds['username'] and password == unit_creds['password']:
                # Salvar informações da sessão
                request.session['authenticated'] = True
                request.session['unit'] = unit
                request.session['username'] = username
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': unit_creds['redirect_page'],
                    'message': f'Login realizado com sucesso para {unit.replace("-", " ").title()}!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Usuário ou senha incorretos'
                }, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Dados inválidos'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Erro interno do servidor'
            }, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

def login_view(request):
    """View de login tradicional (mantida para compatibilidade)"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Usuário ou senha inválidos'})
    return render(request, 'login.html')

def logout_view(request):
    """Logout que limpa a sessão e redireciona para welcome"""
    logout(request)
    request.session.flush()  # Limpa toda a sessão
    return redirect('welcome')

def check_unit_auth(request):
    """Middleware para verificar autenticação por unidade"""
    return request.session.get('authenticated', False)

def get_current_unit(request):
    """Retorna a unidade atual do usuário logado"""
    return request.session.get('unit', None)

def index(request):
    """Página principal - Campos Elísios"""
    if not check_unit_auth(request):
        return redirect('welcome')
    
    # Verificar se é a unidade correta
    current_unit = get_current_unit(request)
    if current_unit != 'campos-elisios':
        return redirect('welcome')
    
    return render(request, 'index.html', {
        'unit': 'Campos Elísios',
        'username': request.session.get('username', '')
    })

def index_jardim_primavera(request):
    """Página principal - Jardim Primavera"""
    if not check_unit_auth(request):
        return redirect('welcome')
    
    # Verificar se é a unidade correta
    current_unit = get_current_unit(request)
    if current_unit != 'jardim-primavera':
        return redirect('welcome')
    
    return render(request, 'index-jardim-primavera.html', {
        'unit': 'Jardim Primavera',
        'username': request.session.get('username', '')
    })

def get_area(id):
    try:
        area = Area.objects.get(id=id)
        return area
    except Area.DoesNotExist:
        return None

@csrf_exempt
def get_estagiarios(request):
    """Retorna estagiários filtrados por unidade se necessário"""
    if not check_unit_auth(request):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    if request.method == 'GET':
        # Aqui você pode filtrar por unidade se necessário
        # Por enquanto, retorna todos os estagiários
        estagiarios = list(Estagiario.objects.values())
        for estagiario in estagiarios:
            area = get_area(estagiario['area_id'])
            estagiario['area'] = area.nome if area else 'Área não encontrada'
        return JsonResponse({'estagiarios': estagiarios}, safe=False)
    
def total_estagiarios_area(area_id):
    return Estagiario.objects.filter(area_id=area_id).count()
    
@csrf_exempt
def get_areas(request):
    """Retorna áreas disponíveis"""
    if not check_unit_auth(request):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    if request.method == 'GET':
        areas = list(Area.objects.values())
        for area in areas:
            area['total_estagiarios'] = total_estagiarios_area(area['id'])
        return JsonResponse({'areas': areas}, safe=False)

@csrf_exempt
def create_area(request):
    """Criar ou editar área"""
    if not check_unit_auth(request):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        area = Area.objects.create(
            nome=data['nome'],
            descricao=data.get('descricao', '')
        )
        return JsonResponse({'id': area.id}, status=201)

    elif request.method == 'PUT':
        data = json.loads(request.body)
        try:
            area = Area.objects.get(id=data['id'])
            area.nome = data['nome']
            area.descricao = data.get('descricao', '')
            area.save()
            return JsonResponse({'message': 'Área atualizada com sucesso!'}, status=200)
        except Area.DoesNotExist:
            return JsonResponse({'error': 'Área não encontrada'}, status=404)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def delete_area(request, area_id):
    """Deletar área"""
    if not check_unit_auth(request):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    if request.method == 'DELETE':
        try:
            area = Area.objects.get(id=area_id)
            area.delete()
            return JsonResponse({'message': 'Área deletada com sucesso!'}, status=200)
        except Area.DoesNotExist:
            return JsonResponse({'error': 'Área não encontrada'}, status=404)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def create_estagiario(request):
    """Criar ou editar estagiário"""
    if not check_unit_auth(request):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        estagiario = Estagiario.objects.create(
            nome=data['nome'],
            email=data['email'],
            telefone=data['telefone'],
            data_inicio=data['dataInicio'],
            area=Area.objects.get(id=data['area']),  
            ativo=data['ativo']
        )
        return JsonResponse({'id': estagiario.id}, status=201)

    elif request.method == 'PUT':
        data = json.loads(request.body)
        try:
            estagiario = Estagiario.objects.get(id=data['id'])
            estagiario.nome = data['nome']
            estagiario.email = data['email']
            estagiario.telefone = data['telefone']
            estagiario.data_inicio = data['dataInicio']
            estagiario.area = Area.objects.get(id=data['area'])
            estagiario.ativo = data['ativo']
            estagiario.save()
            return JsonResponse({'message': 'Estagiário atualizado com sucesso!'}, status=200)
        except Estagiario.DoesNotExist:
            return JsonResponse({'error': 'Estagiário não encontrado'}, status=404)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def delete_estagiario(request, estagiario_id):
    """Deletar estagiário"""
    if not check_unit_auth(request):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    if request.method == 'DELETE':
        try:
            estagiario = Estagiario.objects.get(id=estagiario_id)
            estagiario.delete()
            return JsonResponse({'message': 'Estagiário deletado com sucesso!'}, status=200)
        except Estagiario.DoesNotExist:
            return JsonResponse({'error': 'Estagiário não encontrado'}, status=404)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def get_presencas(request):
    """Retorna presenças"""
    if not check_unit_auth(request):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    if request.method == 'GET':
        presencas = list(Presenca.objects.values(
            'id', 'estagiario_id', 'data', 'entrada', 'saida', 'horas', 'observacao',
            'estagiario__nome'
        ))
        return JsonResponse({'presencas': presencas}, safe=False)
    else:
        return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def registrar_saida(request):
    """Registrar saída do estagiário"""
    if not check_unit_auth(request):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
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
    """Registrar entrada do estagiário"""
    if not check_unit_auth(request):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        estagiario = Estagiario.objects.get(id=data['estagiarioId'])
        entrada = parse_time(data['entrada'])
        presenca = Presenca.objects.create(estagiario=estagiario, data=data['data'], entrada=entrada)
        return JsonResponse({'message': 'Entrada registrada com sucesso!', 'id': presenca.id}, status=201)

def calculadora_horas(request):
    """Calculadora de horas"""
    if not check_unit_auth(request):
        return redirect('welcome')
    return render(request, 'calculadora-hour.html')

@csrf_exempt
def get_user_info(request):
    """Retorna informações do usuário logado"""
    if not check_unit_auth(request):
        return JsonResponse({'error': 'Não autorizado'}, status=401)
    
    return JsonResponse({
        'authenticated': True,
        'unit': get_current_unit(request),
        'username': request.session.get('username', ''),
        'unit_display': get_current_unit(request).replace('-', ' ').title() if get_current_unit(request) else ''
    })