
# filepath: seice/urls.py
from django.contrib import admin
from django.urls import path
from core import views
from core.views import carregar_objetos_controlid

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.index, name='index'),

    path('api/areas/', views.get_areas, name='get_areas'),
    path('api/areas/create/', views.create_area, name='create_area'),
    path('api/areas/<int:area_id>/delete/', views.delete_area, name='delete_area'),

    # ✅ Rota adicionada para a Calculadora de Horas
    path('home/calculadora-horas/', views.calculadora_horas, name='calculadora_horas'),
   
    path('api/estagiarios/', views.get_estagiarios),
    path('api/estagiarios/create/', views.create_estagiario),
    path('api/estagiarios/<int:estagiario_id>/delete/', views.delete_estagiario),

    path('api/presencas/entrada/', views.registrar_entrada),
    path('api/presencas/', views.get_presencas),
    path('api/presencas/saida/', views.registrar_saida),

    # URLs para gerenciamento de usuários
    path('api/usuarios/criar-admin/', views.criar_usuario_admin, name='criar_usuario_admin'),
    path('api/usuarios/', views.get_usuarios, name='get_usuarios'),
    path('api/usuarios/alterar-senha/', views.alterar_senha, name='alterar_senha'),

    # URLs para integração Control ID
    path('api/carregar-objetos/', views.carregar_objetos_controlid, name='carregar_objetos_controlid'),
    path('api/control-id/adicionar/', views.adicionar_control_id_estagiario, name='adicionar_control_id'),
    path('api/control-id/logs/coleta/', views.controlar_coleta_logs, name='controlar_coleta_logs'),
    path('api/control-id/logs/manual/', views.coletar_logs_manual, name='coletar_logs_manual'),
    
    # Sistema SIMPLES de presenças automáticas
    path('api/presencas-auto/status/', views.presencas_automaticas_status, name='presencas_auto_status'),
    path('api/presencas-auto/manual/', views.presencas_automaticas_manual, name='presencas_auto_manual'),
    path('api/presencas-auto/controle/', views.presencas_automaticas_controle, name='presencas_auto_controle'),
]
