from django.contrib import admin
from .models import Dizimista, Igreja, Pagamento
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

from import_export import resources
from import_export.admin import ImportExportModelAdmin

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


class DizimistaResource(resources.ModelResource):
    class Meta:
        model = Dizimista


@admin.register(Dizimista)
class DizimistaAdmin(ImportExportModelAdmin):
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
    resource_class = DizimistaResource


class IgrejaResource(resources.ModelResource):
    class Meta:
        model = Igreja


@admin.register(Igreja)
class IgrejaAdmin(ImportExportModelAdmin):
    list_display = ("nome", "endereco", "número_de_dizimistas")
    search_fields = ["nome"]
    resource_class = IgrejaResource

    def número_de_dizimistas(self, obj):
        return Dizimista.objects.filter(igreja=obj).count()


class PagamentoResource(resources.ModelResource):
    class Meta:
        model = Pagamento


@admin.register(Pagamento)
class PagamentoAdmin(ImportExportModelAdmin):
    resource_class = PagamentoResource
    list_per_page = 20
    list_display = ("data", "valor", "dizimista_link")
    autocomplete_fields = ["igreja", "dizimista"]
    ordering = ["-data"]
    search_fields = ["igreja__nome", "dizimista__nome"]
    list_filter = ["igreja", "data", "registrado_por"]
    readonly_fields = ["data", "registrado_por"]

    def save_model(self, request, obj, form, change):
        print(request.user)
        obj.registrado_por = request.user
        super().save_model(request, obj, form, change)

    def dizimista_link(self, obj):
        dizimista = obj.dizimista
        url = reverse(
            f"admin:{dizimista._meta.app_label}_{dizimista._meta.model_name}_change",
            args=(dizimista.pk,),
        )
        display_text = f"<a href={url}>{dizimista.nome}</a>"
        return format_html(display_text)

    dizimista_link.short_description = "Dizimista"