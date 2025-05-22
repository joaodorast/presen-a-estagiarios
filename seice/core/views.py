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