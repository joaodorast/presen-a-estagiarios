# requirements.txt
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
python-decouple==3.8
Pillow==10.1.0

# settings.py
import os
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Area(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Usuario(AbstractUser):
    TIPO_CHOICES = [
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('rh', 'RH'),
    ]
    
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='usuarios')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='supervisor')
    telefone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return f"{self.get_full_name()} - {self.area.nome}"

class Estagiario(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('finalizado', 'Finalizado'),
    ]

    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=14, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='estagiarios')
    supervisor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='estagiarios_supervisionados')
    curso = models.CharField(max_length=100)
    instituicao = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    carga_horaria_semanal = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(40)])
    carga_horaria_total = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estagiário"
        verbose_name_plural = "Estagiários"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.area.nome}"

    @property
    def horas_cumpridas(self):
        return sum(presenca.horas_trabalhadas for presenca in self.presencas.all())

    @property
    def percentual_conclusao(self):
        if self.carga_horaria_total > 0:
            return min((self.horas_cumpridas / self.carga_horaria_total) * 100, 100)
        return 0

class Presenca(models.Model):
    estagiario = models.ForeignKey(Estagiario, on_delete=models.CASCADE, related_name='presencas')
    data = models.DateField()
    hora_entrada = models.TimeField()
    hora_saida = models.TimeField(null=True, blank=True)
    horas_trabalhadas = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Presença"
        verbose_name_plural = "Presenças"
        unique_together = ['estagiario', 'data']
        ordering = ['-data']

    def __str__(self):
        return f"{self.estagiario.nome} - {self.data}"

    def save(self, *args, **kwargs):
        if self.hora_entrada and self.hora_saida:
            from datetime import datetime, timedelta
            entrada = datetime.combine(self.data, self.hora_entrada)
            saida = datetime.combine(self.data, self.hora_saida)
            
            # Se saída for no dia seguinte
            if saida < entrada:
                saida += timedelta(days=1)
            
            diferenca = saida - entrada
            self.horas_trabalhadas = diferenca.total_seconds() / 3600
        
        super().save(*args, **kwargs)

# core/serializers.py
from rest_framework import serializers
from .models import Area, Usuario, Estagiario, Presenca

class AreaSerializer(serializers.ModelSerializer):
    total_estagiarios = serializers.SerializerMethodField()
    estagiarios_ativos = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = '__all__'

    def get_total_estagiarios(self, obj):
        return obj.estagiarios.count()

    def get_estagiarios_ativos(self, obj):
        return obj.estagiarios.filter(status='ativo').count()

class UsuarioSerializer(serializers.ModelSerializer):
    area_nome = serializers.CharField(source='area.nome', read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 
                 'area', 'area_nome', 'tipo', 'telefone', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class EstagiarioSerializer(serializers.ModelSerializer):
    area_nome = serializers.CharField(source='area.nome', read_only=True)
    supervisor_nome = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    horas_cumpridas = serializers.ReadOnlyField()
    percentual_conclusao = serializers.ReadOnlyField()

    class Meta:
        model = Estagiario
        fields = '__all__'

class EstagiarioCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estagiario
        fields = '__all__'

    def validate(self, data):
        if data['data_inicio'] >= data['data_fim']:
            raise serializers.ValidationError("Data de início deve ser anterior à data de fim.")
        return data

class PresencaSerializer(serializers.ModelSerializer):
    estagiario_nome = serializers.CharField(source='estagiario.nome', read_only=True)

    class Meta:
        model = Presenca
        fields = '__all__'

    def validate(self, data):
        if data.get('hora_saida') and data['hora_entrada'] >= data.get('hora_saida'):
            raise serializers.ValidationError("Hora de entrada deve ser anterior à hora de saída.")
        return data

# core/permissions.py
from rest_framework.permissions import BasePermission

class IsOwnerAreaOrAdmin(BasePermission):
    """
    Permissão que permite acesso apenas aos dados da área do usuário ou admin
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin tem acesso a tudo
        if request.user.tipo == 'admin':
            return True
        
        # Para outros usuários, verificar se o objeto pertence à mesma área
        if hasattr(obj, 'area'):
            return obj.area == request.user.area
        
        # Para estagiários, verificar através da área
        if hasattr(obj, 'estagiario'):
            return obj.estagiario.area == request.user.area
            
        return False

# core/mixins.py
class AreaFilterMixin:
    """
    Mixin para filtrar automaticamente por área do usuário
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Admin vê todos os dados
        if self.request.user.tipo == 'admin':
            return queryset
        
        # Outros usuários veem apenas da sua área
        if hasattr(queryset.model, 'area'):
            return queryset.filter(area=self.request.user.area)
        
        # Para modelos relacionados (como Presenca)
        if hasattr(queryset.model, 'estagiario'):
            return queryset.filter(estagiario__area=self.request.user.area)
        
        return queryset

# core/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Avg, Sum
from datetime import datetime, timedelta
import json

from .models import Area, Usuario, Estagiario, Presenca
from .serializers import (
    AreaSerializer, UsuarioSerializer, EstagiarioSerializer,
    EstagiarioCreateUpdateSerializer, PresencaSerializer
)
from .permissions import IsOwnerAreaOrAdmin
from .mixins import AreaFilterMixin

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        user_area = request.user.area
        
        # Filtrar por área se não for admin
        if request.user.tipo != 'admin':
            estagiarios = Estagiario.objects.filter(area=user_area)
            presencas = Presenca.objects.filter(estagiario__area=user_area)
        else:
            estagiarios = Estagiario.objects.all()
            presencas = Presenca.objects.all()

        # Estatísticas básicas
        stats = {
            'total_estagiarios': estagiarios.count(),
            'estagiarios_ativos': estagiarios.filter(status='ativo').count(),
            'presencas_hoje': presencas.filter(data=datetime.now().date()).count(),
            'horas_trabalhadas_mes': float(
                presencas.filter(
                    data__month=datetime.now().month,
                    data__year=datetime.now().year
                ).aggregate(total=Sum('horas_trabalhadas'))['total'] or 0
            ),
        }

        # Estagiários por status
        stats['estagiarios_por_status'] = list(
            estagiarios.values('status').annotate(
                count=Count('id')
            ).order_by('status')
        )

        # Presença por área (apenas para admin)
        if request.user.tipo == 'admin':
            stats['presencas_por_area'] = list(
                Area.objects.annotate(
                    presencas_count=Count('estagiarios__presencas')
                ).values('nome', 'presencas_count')
            )

        return Response(stats)

class AreaViewSet(AreaFilterMixin, viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated, IsOwnerAreaOrAdmin]

class UsuarioViewSet(AreaFilterMixin, viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, IsOwnerAreaOrAdmin]

class EstagiarioViewSet(AreaFilterMixin, viewsets.ModelViewSet):
    queryset = Estagiario.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerAreaOrAdmin]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EstagiarioCreateUpdateSerializer
        return EstagiarioSerializer

    @action(detail=True, methods=['get'])
    def relatorio(self, request, pk=None):
        estagiario = self.get_object()
        presencas = estagiario.presencas.all()
        
        relatorio = {
            'estagiario': EstagiarioSerializer(estagiario).data,
            'total_presencas': presencas.count(),
            'horas_trabalhadas': float(sum(p.horas_trabalhadas for p in presencas)),
            'media_horas_dia': float(presencas.aggregate(Avg('horas_trabalhadas'))['horas_trabalhadas__avg'] or 0),
            'dias_trabalhados': presencas.count(),
            'percentual_conclusao': estagiario.percentual_conclusao,
        }
        
        return Response(relatorio)

class PresencaViewSet(AreaFilterMixin, viewsets.ModelViewSet):
    queryset = Presenca.objects.all()
    serializer_class = PresencaSerializer
    permission_classes = [IsAuthenticated, IsOwnerAreaOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros adicionais
        estagiario_id = self.request.query_params.get('estagiario', None)
        data_inicio = self.request.query_params.get('data_inicio', None)
        data_fim = self.request.query_params.get('data_fim', None)
        
        if estagiario_id:
            queryset = queryset.filter(estagiario_id=estagiario_id)
        
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
        
        return queryset

    @action(detail=False, methods=['post'])
    def marcar_entrada(self, request):
        estagiario_id = request.data.get('estagiario_id')
        data = request.data.get('data', datetime.now().date())
        hora_entrada = request.data.get('hora_entrada', datetime.now().time())
        
        try:
            estagiario = Estagiario.objects.get(id=estagiario_id)
            
            # Verificar se o usuário pode acessar este estagiário
            if request.user.tipo != 'admin' and estagiario.area != request.user.area:
                return Response(
                    {'error': 'Sem permissão para acessar este estagiário'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            presenca, created = Presenca.objects.get_or_create(
                estagiario=estagiario,
                data=data,
                defaults={'hora_entrada': hora_entrada}
            )
            
            if not created:
                return Response(
                    {'error': 'Entrada já marcada para hoje'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(PresencaSerializer(presenca).data, status=status.HTTP_201_CREATED)
            
        except Estagiario.DoesNotExist:
            return Response(
                {'error': 'Estagiário não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['patch'])
    def marcar_saida(self, request):
        estagiario_id = request.data.get('estagiario_id')
        data = request.data.get('data', datetime.now().date())
        hora_saida = request.data.get('hora_saida', datetime.now().time())
        
        try:
            presenca = Presenca.objects.get(estagiario_id=estagiario_id, data=data)
            
            # Verificar permissão
            if request.user.tipo != 'admin' and presenca.estagiario.area != request.user.area:
                return Response(
                    {'error': 'Sem permissão'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            presenca.hora_saida = hora_saida
            presenca.save()
            
            return Response(PresencaSerializer(presenca).data)
            
        except Presenca.DoesNotExist:
            return Response(
                {'error': 'Entrada não encontrada para hoje'}, 
                status=status.HTTP_404_NOT_FOUND
            )

# core/auth_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username e password são obrigatórios'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.get_full_name(),
                'email': user.email,
                'area': user.area.nome,
                'area_id': user.area.id,
                'tipo': user.tipo,
            }
        })
    else:
        return Response(
            {'error': 'Credenciais inválidas'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'success': True})

@api_view(['GET'])
def user_info(request):
    if request.user.is_authenticated:
        return Response({
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'name': request.user.get_full_name(),
                'email': request.user.email,
                'area': request.user.area.nome,
                'area_id': request.user.area.id,
                'tipo': request.user.tipo,
            }
        })
    else:
        return Response(
            {'error': 'Usuário não autenticado'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, AreaViewSet, UsuarioViewSet, EstagiarioViewSet, PresencaViewSet
from .auth_views import login_view, logout_view, user_info

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'areas', AreaViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'estagiarios', EstagiarioViewSet)
router.register(r'presencas', PresencaViewSet)

urlpatterns = [
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/user/', user_info, name='user_info'),
    path('api/', include(router.urls)),
]

# project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
               
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Area, Usuario, Estagiario, Presenca

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativa', 'created_at']
    list_filter = ['ativa', 'created_at']
    search_fields = ['nome', 'descricao']-

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'area', 'tipo', 'is_active']
    list_filter = ['area', 'tipo', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('area', 'tipo', 'telefone')
        }),
    )

@admin.register(Estagiario)
class EstagiarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'area', 'supervisor', 'status', 'data_inicio', 'data_fim']
    list_filter = ['area', 'status', 'data_inicio']
    search_fields = ['nome', 'email', 'cpf']
    date_hierarchy = 'data_inicio'

@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ['estagiario', 'data', 'hora_entrada', 'hora_saida', 'horas_trabalhadas']
    list_filter = ['data', 'estagiario__area']
    search_fields = ['estagiario__nome']
    date_hierarchy = 'data'

# management/commands/setup_initial_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Area, Usuario

User = get_user_model()

class Command(BaseCommand):
    help = 'Configura dados iniciais do sistema'

    def handle(self, *args, **options):
        # Criar áreas
        areas = [
            {'nome': 'Tecnologia da Informação', 'descricao': 'Área de TI e desenvolvimento'},
            {'nome': 'Recursos Humanos', 'descricao': 'Gestão de pessoas'},
            {'nome': 'Financeiro', 'descricao': 'Controladoria e finanças'},
            {'nome': 'Marketing', 'descricao': 'Marketing e comunicação'},
        ]

        for area_data in areas:
            area, created = Area.objects.get_or_create(
                nome=area_data['nome'],
                defaults={'descricao': area_data['descricao']}
            )
            if created:
                self.stdout.write(f'Área criada: {area.nome}')

        # Criar usuário admin
        area_ti = Area.objects.get(nome='Tecnologia da Informação')
        
        if not Usuario.objects.filter(username='admin').exists():
            admin_user = Usuario.objects.create_superuser(
                username='admin',
                email='admin@empresa.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                area=area_ti,
                tipo='admin'
            )
            self.stdout.write('Usuário admin criado')

        # Criar usuários supervisores
        supervisores = [
            {'username': 'supervisor_ti', 'area': 'Tecnologia da Informação', 'name': 'João Silva'},
            {'username': 'supervisor_rh', 'area': 'Recursos Humanos', 'name': 'Maria Santos'},
            {'username': 'supervisor_fin', 'area': 'Financeiro', 'name': 'Pedro Costa'},
            {'username': 'supervisor_mkt', 'area': 'Marketing', 'name': 'Ana Oliveira'},
        ]

        for supervisor_data in supervisores:
            area = Area.objects.get(nome=supervisor_data['area'])
            
            if not Usuario.objects.filter(username=supervisor_data['username']).exists():
                names = supervisor_data['name'].split()
                usuario = Usuario.objects.create_user(
                    username=supervisor_data['username'],
                    email=f"{supervisor_data['username']}@empresa.com",
                    password='123456',
                    first_name=names[0],
                    last_name=' '.join(names[1:]) if len(names) > 1 else '',
                    area=area,
                    tipo='supervisor'
                )
                self.stdout.write(f'Supervisor criado: {usuario.username}')

        self.stdout.write(
            self.style.SUCCESS('Dados iniciais configurados com sucesso!')
        )

# Comandos para executar:
"""
1. Instalar dependências:
   pip install -r requirements.txt

2. Configurar banco de dados:
   python manage.py makemigrations
   python manage.py migrate

3. Carregar dados iniciais:
   python manage.py setup_initial_data

4. Executar servidor:
   python manage.py runserver

5. URLs disponíveis:
   - Admin: http://localhost:8000/admin/
   - API: http://localhost:8000/api/
   - Login: POST http://localhost:8000/api/auth/login/
   
6. Credenciais:
   - Admin: admin / admin123
   - Supervisores: supervisor_ti / 123456 (e outros)
"""