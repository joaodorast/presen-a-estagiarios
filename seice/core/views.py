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
from datetime import datetime, date

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Redireciona para a página inicial
        else:
            return render(request, 'login.html', {'error': 'Usuário ou senha inválidos'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redireciona para a página de login se não estiver autenticado
    return render(request, 'index.html')

def get_area(id):
    try:
        area = Area.objects.get(id=id)
        return area
    except Area.DoesNotExist:
        return None

@csrf_exempt
def get_estagiarios(request):
    if request.method == 'GET':
        estagiarios = list(Estagiario.objects.values())
        for estagiario in estagiarios:
            area = get_area(estagiario['area_id'])
            estagiario['area'] = area.nome if area else 'Área não encontrada'
            estagiario['temDigital'] = bool(estagiario['digital'])
            print(estagiario['temDigital'])
        return JsonResponse({'estagiarios': estagiarios}, safe=False)
    
def total_estagiarios_area(area_id):
    return Estagiario.objects.filter(area_id=area_id).count()
    
@csrf_exempt
def get_areas(request):
    if request.method == 'GET':
        areas = list(Area.objects.values())
        for area in areas:
            area['total_estagiarios'] = total_estagiarios_area(area['id'])
        return JsonResponse({'areas': areas}, safe=False)
    

@csrf_exempt
def create_area(request):
    if request.method == 'POST':
        # Criar uma nova área
        data = json.loads(request.body)
        area = Area.objects.create(
            nome=data['nome'],
            descricao=data.get('descricao', '')
        )
        return JsonResponse({'id': area.id}, status=201)

    elif request.method == 'PUT':
        # Editar uma área existente
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
    if request.method == 'POST':
        # Criar um novo estagiário
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
        # Editar um estagiário existente
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
    if request.method == 'GET':
        presencas = list(Presenca.objects.values(
            'id', 'estagiario_id', 'data', 'entrada', 'saida', 'horas', 'observacao',
            'estagiario__nome'  # Inclui o nome do estagiário
        ))
        print(presencas)
        return JsonResponse({'presencas': presencas}, safe=False)
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
    

@csrf_exempt
def add_digital(request):
    print(request.method)
    print(request.body)
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            estagiario = Estagiario.objects.get(id=data['estagiarioId'])
            estagiario.digital = data['digital']
            estagiario.save()
            return JsonResponse({'message': 'Digital adicionada com sucesso!'}, status=200)
        except Estagiario.DoesNotExist:
            return JsonResponse({'error': 'Estagiário não encontrado'}, status=404)
    return HttpResponse(
        'Método não permitido. Use POST para adicionar digital.',
        status=405
    )

@csrf_exempt
def bater_ponto(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        digital_recebida = data.get('digital')
        hora_entrada = data.get('entrada')  # opcional, pode usar hora atual
        data_hoje = data.get('data') or date.today().isoformat()

        # Aqui você deve usar sua biblioteca de comparação de digitais
        # Exemplo simples: comparação direta (substitua pela sua lógica real)
        try:
            estagiario = Estagiario.objects.get(digital=digital_recebida)
        except Estagiario.DoesNotExist:
            return JsonResponse({'sucesso': False, 'mensagem': 'Digital não reconhecida!'}, status=404)

        # Verifica se já existe presença aberta hoje para esse estagiário
        ja_presente = Presenca.objects.filter(
            estagiario=estagiario,
            data=data_hoje,
            saida__isnull=True
        ).exists()
        if ja_presente:
            return JsonResponse({'sucesso': False, 'mensagem': 'Estagiário já está presente hoje!'}, status=400)

        # Registra a presença
        if not hora_entrada:
            hora_entrada = datetime.now().strftime('%H:%M:%S')
        entrada = parse_time(hora_entrada)
        presenca = Presenca.objects.create(
            estagiario=estagiario,
            data=data_hoje,
            entrada=entrada
        )
        return JsonResponse({
            'sucesso': True,
            'mensagem': 'Ponto registrado com sucesso!',
            'estagiario_nome': estagiario.nome,
            'id': presenca.id
        }, status=201)
    return HttpResponse(
        'Método não permitido. Use POST para registrar ponto.',
        status=405
    )

#  adiconei uma nova view: 
def calculadora_horas(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'calculadora-hour.html')   
