# filepath: core/views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_time
from .models import Estagiario, Presenca
import json


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def get_estagiarios(request):
    if request.method == 'GET':
        estagiarios = list(Estagiario.objects.values())
        return JsonResponse({'estagiarios': estagiarios}, safe=False)

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
            estagiario.ativo = data['ativo']
            estagiario.save()
            return JsonResponse({'message': 'Estagiário atualizado com sucesso!'}, status=200)
        except Estagiario.DoesNotExist:
            return JsonResponse({'error': 'Estagiário não encontrado'}, status=404)

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