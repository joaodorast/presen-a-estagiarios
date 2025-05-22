# filepath: core/admin.py
from django.contrib import admin
from .models import Estagiario, Presenca

admin.site.register(Estagiario)
admin.site.register(Presenca)