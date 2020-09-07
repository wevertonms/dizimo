import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.utils.timezone import datetime, now
from django.utils.translation import gettext_lazy as _

from .models import Dizimista, Igreja, Pagamento


admin.site.site_header = "DezPorcento"
admin.site.site_title = "DezPorcento"
admin.site.index_title = "Registros"


def igrejas_do_usuário(user):
    gestor_em = Q(gestores__pk=user.pk)
    agente_em = Q(agentes__pk=user.pk)
    return Igreja.objects.filter(agente_em | gestor_em)


def get_permission(model, permission: str):
    model_content_type = ContentType.objects.get_for_model(model)
    model_permissions = Permission.objects.filter(content_type=model_content_type)
    return model_permissions.get(codename__startswith=permission)


def user_str(user: User):
    return f"{user.first_name} {user.last_name} ({user.username})"


# Unregister the provided model admin
admin.site.unregister(User)


def GESTORES_GROUP():
    gestores_group = Group.objects.get_or_create(name="Gestores da pastoral")[0]
    gestores_group.permissions.set(
        (
            get_permission(User, "view"),
            get_permission(User, "change"),
            get_permission(Dizimista, "view"),
            get_permission(Dizimista, "add"),
            get_permission(Dizimista, "change"),
            get_permission(Dizimista, "delete"),
            get_permission(Pagamento, "view"),
            get_permission(Pagamento, "add"),
            get_permission(Pagamento, "change"),
            get_permission(Igreja, "view"),
        )
    )
    gestores_group.save()
    return gestores_group


def AGENTES_GROUP():
    agentes_group = Group.objects.get_or_create(name="Agentes da pastoral")[0]
    agentes_group.permissions.set(
        (
            get_permission(User, "view"),
            get_permission(User, "change"),
            get_permission(Dizimista, "view"),
            get_permission(Dizimista, "add"),
            get_permission(Dizimista, "change"),
            get_permission(Igreja, "view"),
            get_permission(Pagamento, "view"),
            get_permission(Pagamento, "add"),
        )
    )
    agentes_group.save()
    return agentes_group


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ["date_joined"]
    list_filter = []

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        sou_eu = Q(username=user.username)
        # igrejas = igrejas_do_usuário(user)
        # agentes = Q(agente_em__in=igrejas)
        # gestores = Q(gestor_em__in=igrejas)
        return qs.filter(sou_eu)

    def get_form(self, request: HttpRequest, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set(["last_login"])
        if not is_superuser:
            if request.user == obj:
                disabled_fields |= {
                    "username",
                    "is_active",
                    "is_superuser",
                    "is_staff",
                    "groups",
                    "user_permissions",
                }
            else:
                disabled_fields = set(form.base_fields)
        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True
        return form

    def save_model(self, request: HttpRequest, obj: User, form, change):
        obj.registrado_por = request.user
        is_new_user = not obj.pk
        if is_new_user:
            obj.is_staff = True
        super().save_model(request, obj, form, change)
        if is_new_user:
            new_user_permissions = [
                get_permission(User, "view"),
                get_permission(User, "change"),
            ]
            obj.user_permissions.set(new_user_permissions)


class ExportCsvMixin:
    def export_as_csv(self, request: HttpRequest, queryset):
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


class DataMonthListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Mês")
    # Parameter for the filter that will be used in the URL query.
    parameter_name = "mes"
    field = "data__month"

    def lookups(self, request: HttpRequest, model_admin):  # noqa
        """Returns a list of tuples. The first element in each tuple is the coded value
        for the option that will appear in the URL query. The second element is the
        human-readable name for the option that will appear in the right sidebar.
        """
        return [(i, _(datetime(1, i, 1).strftime("%B"))) for i in range(1, 13)]

    def queryset(self, request: HttpRequest, queryset):
        """Returns the filtered queryset based on the value provided in the query
        string and retrievable via `self.value()`.
        """
        if self.value():
            filter_kwargs = {self.field: self.value()}
            return queryset.filter(**filter_kwargs)
        return queryset


class AniversarioMesListFilter(DataMonthListFilter):
    title = _("Anversariante do mês")
    parameter_name = "aniversario_mes"
    field = "nascimento__month"


def endereco(obj):
    return f"{obj.endereco[:30]} ..."


class PagamentoInline(admin.TabularInline):
    model = Pagamento
    view_on_site = False
    extra = 0


class IgrejaListFilter(admin.SimpleListFilter):
    title = _("Igreja")
    parameter_name = "igreja"

    def lookups(self, request: HttpRequest, model_admin):  # noqa
        user = request.user
        if user.is_superuser:
            igrejas = Igreja.objects.all()
        else:
            igrejas = igrejas_do_usuário(user)
        return [(i.pk, i) for i in igrejas]

    def queryset(self, request: HttpRequest, queryset):
        if self.value():
            return queryset.filter(igreja__pk=self.value())
        return queryset


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
    search_fields = ["nome"]
    list_filter = [IgrejaListFilter, "genero", AniversarioMesListFilter]
    actions = ["export_as_csv"]
    autocomplete_fields = ["igreja"]
    inlines = (PagamentoInline,)

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        gestor_em = Q(gestores__pk=user.pk)
        agente_em = Q(agentes__pk=user.pk)
        igrejas = Igreja.objects.filter(agente_em | gestor_em)
        return qs.filter(igreja__in=igrejas)


class DizimistaInline(admin.TabularInline):
    model = Dizimista
    exclude = ("nome",)
    view_on_site = False


@admin.register(Igreja)
class IgrejaAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        "nome",
        "endereco",
        "gestores_da_patoral",
        "agentes_da_pastoral",
        "número_de_dizimistas",
    )
    search_fields = ["nome"]
    actions = ["export_as_csv"]
    filter_horizontal = ("gestores", "agentes")
    inlines = [DizimistaInline]

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        return igrejas_do_usuário(user)

    def gestores_da_patoral(self, obj: Igreja):
        display_text = []
        for user in obj.gestores.all():
            display_text.append(user_str(user))
        return ", ".join(display_text)

    def agentes_da_pastoral(self, obj: Igreja):
        display_text = []
        for user in obj.agentes.all():
            display_text.append(user_str(user))
        return ", ".join(display_text)


class RegistradoPorListFilter(admin.SimpleListFilter):
    title = _("Registrado Por")
    parameter_name = "registrado_por"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin):  # noqa
        registradores = set(
            p.registrado_por for p in model_admin.get_queryset(request).all()
        )
        return [(r.pk, user_str(r)) for r in registradores]

    def queryset(self, request: HttpRequest, queryset):
        if self.value():
            return queryset.filter(registrado_por__pk=self.value())
        return queryset


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin, ExportCsvMixin):
    fields = ("igreja", "dizimista", "valor", "data", "registrado_por")
    list_per_page = 20
    list_display = ["data", "valor", "dizimista_link"]
    list_select_related = True
    autocomplete_fields = ["igreja", "dizimista"]
    search_fields = ["igreja__nome", "dizimista__nome"]
    list_filter = [
        IgrejaListFilter,
        "data",
        DataMonthListFilter,
        RegistradoPorListFilter,
    ]
    actions = ["export_as_csv"]

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if request.user.is_superuser:
            return []
        return ["data", "registrado_por", "id"]

    def save_model(self, request: HttpRequest, obj, form, change):
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
        return obj.dizimista.link()

    dizimista_link.short_description = "Dizimista"

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        igrejas = igrejas_do_usuário(user)
        return qs.filter(igreja__in=igrejas)
