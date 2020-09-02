from django.contrib import admin
from .models import Dizimista, Igreja, Pagamento


@admin.register(Dizimista)
class DizimistaAdmin(admin.ModelAdmin):
    list_display = ("nome", "endereco", "telefone", "nascimento")
    search_fields = ["nome"]


@admin.register(Igreja)
class IgrejaAdmin(admin.ModelAdmin):
    list_display = ("nome", "endereco")
    search_fields = ["nome"]


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "valor", "igreja", "dizimista")
    search_fields = ["id", "data", "igreja", "dizimista"]
    list_filter = ["igreja", "data"]