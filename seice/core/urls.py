# filepath: seice/urls.py
from django.contrib import admin
from django.urls import path
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.index, name='index'),



    path('api/estagiarios/', views.get_estagiarios),
    path('api/estagiarios/create/', views.create_estagiario),

    path('api/estagiarios/<int:estagiario_id>/delete/', views.delete_estagiario),

    path('api/presencas/entrada/', views.registrar_entrada),
    path('api/presencas/', views.get_presencas),
    path('api/presencas/saida/', views.registrar_saida),
]