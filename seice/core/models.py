# filepath: core/models.py
from django.db import models


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    login = models.CharField(max_length=100, unique=True)
    senha = models.CharField(max_length=100)

class Unidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome
    
class UsuarioUnidade(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE)
    nivel_acesso = models.CharField(max_length=50, choices=[('leitura', 'Leitura'), ('admin', 'Admin')])


class Estagiario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    setor = models.CharField(max_length=100, choices=[('tecnologia', 'Tecnologia'), ('financeiro', 'Financeiro'), ('pedagogia', 'Pedagogia'), ('educação física', 'Educação Física')])
    area = models.ForeignKey('Area', on_delete=models.CASCADE, related_name='estagiarios')
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='estagiarios')
    # matricula = models.CharField(max_length=20, unique=True)
    # Campos para integração com Control ID
    control_id_user_id = models.CharField(max_length=50, blank=True, null=True, help_text="ID do usuário no Control ID")
    presente = models.BooleanField(default=False, help_text="Indica se o estagiário está presente (True) ou ausente (False)")
    data_inicio = models.DateField()
    efetivado = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    
    def tem_control_id(self):
        return bool(self.control_id_user_id)

class Area(models.Model):
    nome = models.CharField(max_length=100)
    setor = models.CharField(max_length=100, choices=[('tecnologia', 'Tecnologia'), ('financeiro', 'Financeiro'), ('pedagogia', 'Pedagogia'), ('educação física', 'Educação Física')])
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='areas')

    def __str__(self):
        return self.nome


class Presenca(models.Model):
    estagiario = models.ForeignKey(Estagiario, on_delete=models.CASCADE)
    data = models.DateField()
    entrada = models.TimeField(null=True, blank=True)
    saida = models.TimeField(null=True, blank=True)
    horas = models.CharField(max_length=10, null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"{self.estagiario.nome} - {self.data} - {'Presente' if self.estagiario.presente else 'Ausente'}"
    

class ControleColetaLogs(models.Model):
    ultimo_timestamp = models.DateTimeField(null=True, blank=True, help_text="Timestamp do último log processado")
    ultimo_log_id = models.CharField(max_length=32, null=True, blank=True, help_text="ID único do último log processado")
    total_processados = models.IntegerField(default=0, help_text="Total de logs processados")
    processed_log_ids = models.JSONField(default=list, help_text="Lista de IDs de logs já processados (cache)")

    class Meta:
        verbose_name = "Controle de Coleta de Logs"
        verbose_name_plural = "Controles de Coleta de Logs"

    def __str__(self):
        return f"Controle Coleta Logs - Último: {self.ultimo_timestamp}"
    

    