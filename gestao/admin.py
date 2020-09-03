from django.contrib import admin
from .models import Dizimista, Igreja, Pagamento
from django.utils.translation import gettext_lazy as _

admin.site.site_header = "DezPorcento"
admin.site.site_title = "DezPorcento"
admin.site.index_title = "Registros"


class AniversarioMesListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Anversariante do mês")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "aniversario_mes"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("1", _("Janeiro")),
            ("2", _("Fevereiro")),
            ("3", _("Março")),
            ("4", _("Abril")),
            ("5", _("Maio")),
            ("6", _("Junho")),
            ("7", _("Julho")),
            ("8", _("Agosto")),
            ("9", _("Setembro")),
            ("10", _("Outrubro")),
            ("11", _("Novembro")),
            ("12", _("Dezembro")),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(nascimento__month=self.value())
        return queryset


def endereco(obj):
    return f"{obj.endereco[:30]} ..."


@admin.register(Dizimista)
class DizimistaAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        "nome",
        "nascimento",
        endereco,
        "telefone",
    )
    ordering = ["nome"]
    autocomplete_fields = ["igreja"]
    search_fields = ["nome"]
    list_filter = ["igreja", "genero", AniversarioMesListFilter]


def número_de_dizimistas(obj):
    return Dizimista.objects.filter(igreja=obj).count()


@admin.register(Igreja)
class IgrejaAdmin(admin.ModelAdmin):
    list_display = ("nome", "endereco", número_de_dizimistas)
    search_fields = ["nome"]


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ("data", "valor", "igreja", "dizimista")
    autocomplete_fields = ["igreja", "dizimista"]
    ordering = ["data"]
    search_fields = ["igreja__nome", "dizimista__nome"]
    list_filter = ["igreja", "data", "registrado_por"]
    readonly_fields = ["data", "registrado_por"]