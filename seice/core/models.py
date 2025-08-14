# filepath: core/models.py
from django.db import models

class Estagiario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    area = models.ForeignKey('Area', on_delete=models.CASCADE, related_name='estagiarios')
    digital = models.CharField(max_length=500, default='')
    telefone = models.CharField(max_length=20)
    data_inicio = models.DateField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Area(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome



class Presenca(models.Model):
    estagiario = models.ForeignKey(Estagiario, on_delete=models.CASCADE)
    data = models.DateField()
    entrada = models.TimeField()
    saida = models.TimeField(null=True, blank=True)
    horas = models.CharField(max_length=10, null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.estagiario.nome} - {self.data}"
    

class PushCommand(models.Model):
    device_id = models.CharField(max_length=64)
    uuid = models.CharField(max_length=128)
    verb = models.CharField(max_length=10, blank=True, null=True)
    endpoint = models.CharField(max_length=128, blank=True, null=True)
    body = models.JSONField(blank=True, null=True)
    content_type = models.CharField(max_length=50, blank=True, null=True)
    query_string = models.CharField(max_length=256, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ResultCommand(models.Model):
    device_id = models.CharField(max_length=64)
    uuid = models.CharField(max_length=128)
    endpoint = models.CharField(max_length=128, blank=True, null=True)
    response = models.JSONField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    

    