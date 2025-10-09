# filepath: core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Estagiario, Presenca, Area, Usuario, ControleColetaLogs, Unidade, UsuarioUnidade

# Cabeçalho em PT-BR
admin.site.site_header = "SEICE — Administração"
admin.site.site_title = "SEICE"
admin.site.index_title = "Painel de Administração"

# CSS embutido simples e leve (injetado nas views do admin)
_CUSTOM_ADMIN_CSS = """
/* SEICE admin - estilos embutidos */
#header, .module h2, .breadcrumbs { font-family: "Segoe UI", Roboto, Arial, sans-serif; }
.change-list .results th { background:#f5f7fa; color:#222; font-weight:600; padding:8px; }
.change-list .results td { padding:10px 12px; vertical-align:middle; }
.field-preview { max-width:320px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.button-inline { margin-right:6px; border-radius:6px; padding:6px 8px; }
.btn-icon { width:34px; height:34px; display:inline-flex; align-items:center; justify-content:center; border-radius:8px; border:none; }
.btn-icon.edit { background:#fff7e6; color:#f6b100; }
.btn-icon.delete { background:#fdeaea; color:#dc3545; }
@media (max-width:800px){ .change-list .results td:nth-child(3){display:none;} }
"""

def _inject_css_into_response(response, css):
    try:
        content_type = response.get('Content-Type', '')
        if response.status_code == 200 and 'text/html' in content_type:
            content = response.content.decode(response.charset or 'utf-8')
            if '</head>' in content:
                content = content.replace('</head>', f'<style>{css}</style></head>', 1)
                response.content = content.encode(response.charset or 'utf-8')
    except Exception:
        pass
    return response

# Area admin — usa método seguro para descricao
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'unidade', 'setor')
    search_fields = ('nome',)
    list_per_page = 25

    def descricao_safe(self, obj):
        return getattr(obj, 'descricao', '-') or '-'
    descricao_safe.short_description = 'Descrição'

    def changelist_view(self, request, extra_context=None):
        resp = super().changelist_view(request, extra_context=extra_context)
        return _inject_css_into_response(resp, _CUSTOM_ADMIN_CSS)
    def change_view(self, request, object_id, form_url='', extra_context=None):
        resp = super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)
        return _inject_css_into_response(resp, _CUSTOM_ADMIN_CSS)

# Unidade admin — campos seguros
@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade_safe', 'ativo_safe')
    search_fields = ('nome','cidade')
    list_per_page = 25

    def cidade_safe(self, obj):
        return getattr(obj, 'cidade', '-') or '-'
    cidade_safe.short_description = 'Cidade'

    def ativo_safe(self, obj):
        val = getattr(obj, 'ativo', None)
        return 'Sim' if val else 'Não'
    ativo_safe.short_description = 'Ativo'

    def changelist_view(self, request, extra_context=None):
        resp = super().changelist_view(request, extra_context=extra_context)
        return _inject_css_into_response(resp, _CUSTOM_ADMIN_CSS)

# Usuario admin — tenta username/email, alternativa nome/email
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username_safe', 'email_safe', 'is_staff_safe')
    search_fields = ('username','email')
    list_per_page = 25

    def username_safe(self, obj):
        return getattr(obj, 'username', getattr(obj, 'nome', '-')) or '-'
    username_safe.short_description = 'Usuário'

    def email_safe(self, obj):
        return getattr(obj, 'email', '-') or '-'
    email_safe.short_description = 'E-mail'

    def is_staff_safe(self, obj):
        val = getattr(obj, 'is_staff', None)
        return 'Sim' if val else 'Não'
    is_staff_safe.short_description = 'Staff'

    def changelist_view(self, request, extra_context=None):
        resp = super().changelist_view(request, extra_context=extra_context)
        return _inject_css_into_response(resp, _CUSTOM_ADMIN_CSS)

# UsuarioUnidade admin — perfil seguro
@admin.register(UsuarioUnidade)
class UsuarioUnidadeAdmin(admin.ModelAdmin):
    list_display = ('usuario_safe', 'unidade_safe', 'perfil_safe')
    search_fields = ('usuario__username','unidade__nome')
    list_per_page = 25

    def usuario_safe(self, obj):
        u = getattr(obj, 'usuario', None)
        return getattr(u, 'username', getattr(u, 'nome', '-')) if u else '-'
    usuario_safe.short_description = 'Usuário'

    def unidade_safe(self, obj):
        un = getattr(obj, 'unidade', None)
        return getattr(un, 'nome', '-') if un else '-'
    unidade_safe.short_description = 'Unidade'

    def perfil_safe(self, obj):
        return getattr(obj, 'perfil', getattr(obj, 'role', '-')) or '-'
    perfil_safe.short_description = 'Perfil'

    def changelist_view(self, request, extra_context=None):
        resp = super().changelist_view(request, extra_context=extra_context)
        return _inject_css_into_response(resp, _CUSTOM_ADMIN_CSS)

# # ControleColetaLogs admin — campos seguros e usuário
# @admin.register(ControleColetaLogs)
# class ControleColetaLogsAdmin(admin.ModelAdmin):
#     list_display = ('id', 'evento_safe', 'timestamp_safe', 'usuario_repr')
#     search_fields = ('evento',)
#     list_per_page = 40

#     def evento_safe(self, obj):
#         return getattr(obj, 'evento', getattr(obj, 'event', '-')) or '-'
#     evento_safe.short_description = 'Evento'

#     def timestamp_safe(self, obj):
#         return getattr(obj, 'timestamp', getattr(obj, 'created_at', '-')) or '-'
#     timestamp_safe.short_description = 'Data / Hora'

#     def usuario_repr(self, obj):
#         u = getattr(obj, 'usuario', None)
#         if not u:
#             return '-'
#         return getattr(u, 'username', getattr(u, 'nome', str(u)))
#     usuario_repr.short_description = 'Usuário'

#     def changelist_view(self, request, extra_context=None):
#         resp = super().changelist_view(request, extra_context=extra_context)
#         return _inject_css_into_response(resp, _CUSTOM_ADMIN_CSS)

# Estagiario and Presenca admins (mantidos com injeção de CSS)
@admin.register(Estagiario)
class EstagiarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'area', 'unidade', 'email', 'ativo', 'control_id_user_id', 'data_inicio_fmt')
    list_display_links = ('nome',)
    list_editable = ('ativo', 'control_id_user_id')
    list_filter = ('ativo', 'area', 'unidade')
    search_fields = ('nome', 'email', 'control_id_user_id')
    ordering = ('nome',)
    readonly_fields = ('id',)
    list_per_page = 25
    list_select_related = ('area', 'unidade')
    fieldsets = (
        (None, {'fields': ('nome', 'email', 'area', 'unidade', 'data_inicio', 'ativo')}),
        ('Controle (Control ID)', {'fields': ('control_id_user_id',), 'classes': ('collapse',)}),
    )

    def data_inicio_fmt(self, obj):
        return obj.data_inicio.strftime('%d/%m/%Y') if obj.data_inicio else '-'
    data_inicio_fmt.short_description = 'Início'

    def changelist_view(self, request, extra_context=None):
        resp = super().changelist_view(request, extra_context=extra_context)
        return _inject_css_into_response(resp, _CUSTOM_ADMIN_CSS)
    def change_view(self, request, object_id, form_url='', extra_context=None):
        resp = super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)
        return _inject_css_into_response(resp, _CUSTOM_ADMIN_CSS)

@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ('estagiario', 'data', 'entrada', 'saida', 'horas_formatadas', 'observacao')
    list_filter = ('data', 'estagiario__area')
    search_fields = ('estagiario__nome',)
    ordering = ('-data',)
    date_hierarchy = 'data'
    list_per_page = 25
    list_select_related = ('estagiario',)

    def horas_formatadas(self, obj):
        h = obj.horas or ''
        if isinstance(h, (int, float)):
            horas = int(h)
            minutos = round((h - horas) * 60)
            return f"{horas}h {minutos}min"
        if isinstance(h, str) and ':' in h:
            hh, mm = h.split(':')[:2]
            return f"{int(hh)}h {int(mm)}min"
        return h or '-'
    horas_formatadas.short_description = 'Tempo'

    actions = ['marcar_confirmada']
    def marcar_confirmada(self, request, queryset):
        queryset.update(observacao='Confirmada pelo admin')
    marcar_confirmada.short_description = "Marcar presença como confirmada"

    def changelist_view(self, request, extra_context=None):
        resp = super().changelist_view(request, extra_context=extra_context)
        return _inject_css_into_response(resp, _CUSTOM_ADMIN_CSS)
    def change_view(self, request, object_id, form_url='', extra_context=None):
        resp = super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)
        return _inject_css_into_response(resp, _CUSTOM_ADMIN_CSS)