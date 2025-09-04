# filepath: core/admin.py
from django.contrib import admin
from .models import Estagiario, Presenca, Area, Usuario, ControleColetaLogs, Unidade, UsuarioUnidade

admin.site.register(Estagiario)
admin.site.register(Presenca)
admin.site.register(Area)
admin.site.register(Usuario)
admin.site.register(ControleColetaLogs)
admin.site.register(Unidade)
admin.site.register(UsuarioUnidade)
