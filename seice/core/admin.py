# filepath: core/admin.py
from django.contrib import admin
from .models import Estagiario, Presenca, Area, PushCommand, ResultCommand

admin.site.register(Estagiario)
admin.site.register(Presenca)
admin.site.register(Area)
admin.site.register(PushCommand)
admin.site.register(ResultCommand)