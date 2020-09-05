import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import datetime, now
from django.utils.translation import gettext_lazy as _

from .models import Dizimista, Igreja, Pagamento, RelatorioPagamentos

admin.site.site_header = "DezPorcento"
admin.site.site_title = "DezPorcento"
admin.site.index_title = "Registros"


def create_igrejas():
    Igreja.objects.create(
        nome="Capela de Nossa Senhora de Quadalupe",
        endereco="Conjunto Virgem dos Pobres III, s/n",
    )
    Igreja.objects.create(
        nome="Capela de Santa Teresinha",
        endereco="Praça Tenente Moisés Silva Filho, s/n",
    )
    Igreja.objects.create(
        nome="Igreja de Nossa Senhora do Virgem dos Pobres",
        endereco="Conjunto Joaquim Leão, s/n",
    )


def get_permission(model, permission: str):
    model_content_type = ContentType.objects.get_for_model(model)
    model_permissions = Permission.objects.filter(content_type=model_content_type)
    return model_permissions.get(codename__startswith=permission)


# Unregister the provided model admin
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ["date_joined"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(username=request.user.username)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set(["last_login"])
        if not is_superuser:
            disabled_fields |= {
                "username",
                "is_active",
                "is_superuser",
                "is_staff",
                "groups",
                "user_permissions",
            }
        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True
        return form

    def save_model(self, request, obj: User, form, change):
        obj.registrado_por = request.user
        is_new_user = not obj.pk
        if is_new_user:
            obj.is_staff = True
        super().save_model(request, obj, form, change)
        if is_new_user:
            new_user_permissions = [
                get_permission(User, "view"),
                get_permission(User, "change"),
                get_permission(Pagamento, "view"),
                get_permission(Pagamento, "add"),
            ]
            obj.user_permissions.set(new_user_permissions)


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type="text/csv")
        filename = f'{str(meta).replace(".", "_")}s_{now().strftime("%Y_%m_%d")}'
        response["Content-Disposition"] = f"attachment; filename={filename}.csv"
        writer = csv.writer(response)
        writer.writerow([field.verbose_name for field in meta.fields])
        for obj in queryset:
            _ = writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = "Exportar como CSV"


def filter_month_by_lookups(self, request, model_admin):  # noqa
    """Returns a list of tuples. The first element in each tuple is the coded value
    for the option that will appear in the URL query. The second element is the
    human-readable name for the option that will appear in the right sidebar.
    """
    return [(i, _(datetime(1, i, 1).strftime("%B"))) for i in range(1, 13)]


def filter_month_by_queryset(self, request, queryset, field):
    """Returns the filtered queryset based on the value provided in the query
    string and retrievable via `self.value()`.
    """
    if self.value():
        filter_kwargs = {field: self.value()}
        return queryset.filter(**filter_kwargs)
    return queryset


class MesListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Mês")
    # Parameter for the filter that will be used in the URL query.
    parameter_name = "mes"
    field = "data__month"

    def lookups(self, request, model_admin):
        return filter_month_by_lookups(self, request, model_admin)

    def queryset(self, request, queryset):
        return filter_month_by_queryset(self, request, queryset, field=self.field)


class AniversarioMesListFilter(MesListFilter):
    title = _("Anversariante do mês")
    parameter_name = "aniversario_mes"
    field = "nascimento__month"


def endereco(obj):
    return f"{obj.endereco[:30]} ..."


@admin.register(Dizimista)
class DizimistaAdmin(admin.ModelAdmin, ExportCsvMixin):
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
    actions = ["export_as_csv"]


@admin.register(Igreja)
class IgrejaAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("nome", endereco, "número_de_dizimistas")
    search_fields = ["nome"]
    actions = ["export_as_csv"]

    def número_de_dizimistas(self, obj):
        return Dizimista.objects.filter(igreja=obj).count()


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin, ExportCsvMixin):
    fields = ("igreja", "dizimista", "valor", "data", "registrado_por")
    list_per_page = 20
    list_display = ("data", "valor", "dizimista_link")
    autocomplete_fields = ["igreja", "dizimista"]
    ordering = ["-data"]
    search_fields = ["igreja__nome", "dizimista__nome"]
    list_filter = ["igreja", "data", "registrado_por", MesListFilter]
    actions = ["export_as_csv"]

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ["data", "registrado_por", "id"]

    def save_model(self, request, obj, form, change):
        obj.registrado_por = request.user
        super().save_model(request, obj, form, change)
        try:
            destinatários = [request.user.mail]
            send_mail(
                subject="Pagamento adicionado",
                message=f"""
    Dizimista: {obj.dizimista}
    Igreja: {obj.igreja}
    Data: {obj.data}
    Valor: {obj.valor}
    Registrado_por: {obj.registrado_por}
    Código do pagamento: {obj.id}
    """,
                from_email="naoresponda@dezporcento.com",
                recipient_list=destinatários,
                fail_silently=True,
            )
        except Exception as e:
            print(e)

    def dizimista_link(self, obj):
        dizimista = obj.dizimista
        url = reverse(
            f"admin:{dizimista._meta.app_label}_{dizimista._meta.model_name}_change",
            args=(dizimista.pk,),
        )
        display_text = f"<a href={url}>{dizimista.nome}</a>"
        return format_html(display_text)

    dizimista_link.short_description = "Dizimista"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if not request.user.is_superuser:
        # return qs.filter(registrado_por=request.user)
        return qs


# @admin.register(RelatorioPagamentos)
# class RelatorioPagamentosAdmin(admin.ModelAdmin):
#     pass
