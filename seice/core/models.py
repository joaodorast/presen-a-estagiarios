# filepath: core/models.py
from django.db import models

class Estagiario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    data_inicio = models.DateField()
    ativo = models.BooleanField(default=True)

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