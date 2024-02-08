import pdfkit
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek, TruncYear
from django.http import FileResponse, HttpRequest
from django.template.loader import render_to_string
from django.utils.timezone import datetime, now, timedelta
from django.utils.translation import gettext_lazy as _

from core.admin import get_permission
from core.models import Perfil
from dizimo.settings import EMAIL_HOST_USER

from .models import Dizimista, Igreja, Pagamento, PerfilDizimista, ResumoPagamentos

admin.site.site_header = "DezPorcento"
admin.site.site_title = "DezPorcento"
admin.site.index_title = "Registros"


def GESTORES_GROUP():
    gestores_group = Group.objects.get_or_create(name="Gestores da pastoral")[0]
    gestores_group.permissions.set(
        (
            get_permission(User, "view"),
            get_permission(User, "change"),
            get_permission(Perfil, "view"),
            get_permission(Perfil, "add"),
            get_permission(Perfil, "change"),
            get_permission(Dizimista, "view"),
            get_permission(Dizimista, "add"),
            get_permission(Dizimista, "change"),
            get_permission(Dizimista, "delete"),
            get_permission(PerfilDizimista, "view"),
            get_permission(PerfilDizimista, "add"),
            get_permission(PerfilDizimista, "change"),
            get_permission(Igreja, "view"),
            get_permission(Igreja, "change"),
            get_permission(Pagamento, "view"),
            get_permission(Pagamento, "add"),
            get_permission(Pagamento, "change"),
            get_permission(ResumoPagamentos, "view"),
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
            get_permission(Perfil, "view"),
            get_permission(Perfil, "add"),
            get_permission(Perfil, "change"),
            get_permission(Dizimista, "view"),
            get_permission(Dizimista, "add"),
            get_permission(Dizimista, "change"),
            get_permission(PerfilDizimista, "view"),
            get_permission(PerfilDizimista, "add"),
            get_permission(PerfilDizimista, "change"),
            get_permission(Igreja, "view"),
            get_permission(Pagamento, "view"),
            get_permission(Pagamento, "add"),
            get_permission(ResumoPagamentos, "view"),
        )
    )
    agentes_group.save()
    return agentes_group


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ["nome", "user"]
    sortable_by = list_display
    search_fields = ["nome", "user"]

    def get_readonly_fields(self, request: HttpRequest, obj: PerfilDizimista):  # noqa
        fields = ["user"]
        user = request.user
        is_superuser = user.is_superuser
        if not is_superuser:
            if hasattr(obj, "user"):
                if obj.user != user:
                    fields += [
                        "nome",
                        "endereco",
                        "nascimento",
                        "genero",
                        "telefone",
                        "email",
                        "dizimista",
                    ]
            return fields
        return ()

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        return qs.filter(user=user)


def igrejas_do_usuário(user):
    gestor_em = Q(gestores__pk=user.pk)
    agente_em = Q(agentes__pk=user.pk)
    return Igreja.objects.filter(agente_em | gestor_em).distinct()


def dizimistas_do_usuário(user):
    qs = Dizimista.objects.all()  # super().get_queryset(request)
    if user.is_superuser:
        return qs
    igrejas = igrejas_do_usuário(user)
    return qs.filter(igreja__in=igrejas)


class ExportPdfMixin:
    def export_as_pdf(self, request: HttpRequest, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        headers = [field.verbose_name for field in meta.fields]
        title = str(meta).split(".")[1] + "s"
        filename = f'{title}_{now().strftime("%Y_%m_%d")}.pdf'
        data = [
            {field: getattr(obj, field) for field in field_names} for obj in queryset
        ]
        html = render_to_string(
            "admin/export_as_pdf.html",
            dict(title=title.title(), headers=headers, data=data),
        )
        options = {
            "page-size": "A4",
            "margin-top": "2cm",
            "margin-right": "1cm",
            "margin-bottom": "1cm",
            "margin-left": "2cm",
            "encoding": "UTF-8",
        }
        pdfkit.from_string(html, filename, options=options)
        return FileResponse(open(filename, "rb"), as_attachment=False)

    export_as_pdf.short_description = "Exportar dados em PDF"


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
    field = "perfil__nascimento__month"


def endereco(obj):
    return f"{obj.endereco[:30]} ..."


class PerfilDizimistaInline(admin.StackedInline):
    model = PerfilDizimista
    can_delete = False
    view_on_site = False
    verbose_name_plural = "Perfil"
    autocomplete_fields = ["user"]
    extra = 1
    fields = ["nome", "endereco", "nascimento", "genero", "telefone", "email"]

    def get_readonly_fields(self, request: HttpRequest, obj: PerfilDizimista):  # noqa
        fields = []
        user = request.user
        is_superuser = user.is_superuser
        if not is_superuser:
            if hasattr(obj, "perfil"):
                if hasattr(obj.perfil, "user"):
                    if obj.perfil.user:
                        fields += [
                            "nome",
                            "endereco",
                            "nascimento",
                            "genero",
                            "telefone",
                            "email",
                            "user",
                        ]
            return fields
        return ()


class PagamentoInline(admin.TabularInline):
    model = Pagamento
    view_on_site = False
    extra = 1
    fields = ("data", "valor", "registrado_por")
    readonly_fields = ("data", "registrado_por")

    def save_model(self, request: HttpRequest, obj, form, change):
        obj.registrado_por = request.user
        super().save_model(request, obj, form, change)
        try:
            destinatários = []
            if obj.dizimista.email:
                destinatários.append(obj.dizimista.email)
            send_mail(
                subject="Registro de pagamento",
                message="",
                html_message=render_to_string("pagamento.html/", dict(obj=obj)),
                from_email=EMAIL_HOST_USER,
                recipient_list=destinatários,
                fail_silently=False,
            )
            self.message_user(request, "E-mails enviados com sucesso.", level="success")
        except Exception as e:
            print(e)
            self.message_user(request, "Erro ao enviar e-mail", level="error")


class IgrejaListFilter(admin.SimpleListFilter):
    title = _("Igreja")
    parameter_name = "igreja"
    field = "igreja__pk"

    def lookups(self, request: HttpRequest, model_admin):  # noqa
        user = request.user
        if user.is_superuser:
            igrejas = Igreja.objects.all()
        else:
            igrejas = igrejas_do_usuário(user)
        return [(i.pk, i) for i in igrejas]

    def queryset(self, request: HttpRequest, queryset):
        if self.value():
            return queryset.filter(**{self.field: self.value()})
        return queryset


class UltimoPagamentoListFilter(admin.SimpleListFilter):
    title = _("Último Pagamento")
    parameter_name = "ultimopagamento"

    def lookups(self, request: HttpRequest, model_admin):  # noqa
        return [(i, _(f"{i} dias atrás")) for i in [30, 60, 90]]

    def queryset(self, request: HttpRequest, queryset):
        if self.value():
            dias_atras = now() - timedelta(days=int(self.value()) + 1)
            return queryset.exclude(pagamento__data__gt=dias_atras)
        return queryset


@admin.register(Dizimista)
class DizimistaAdmin(admin.ModelAdmin, ExportPdfMixin):
    actions_selection_counter = False
    list_per_page = 20
    list_select_related = True
    list_display = ["perfil", "nascimento", "igreja"]
    sortable_by = list_display
    search_fields = ["perfil__nome"]
    list_filter = [
        IgrejaListFilter,
        "perfil__genero",
        AniversarioMesListFilter,
        UltimoPagamentoListFilter,
    ]
    actions = ["export_as_pdf"]
    autocomplete_fields = ["igreja"]
    inlines = [
        PerfilDizimistaInline,
        PagamentoInline,
    ]

    def get_queryset(self, request: HttpRequest):
        return dizimistas_do_usuário(user=request.user)


class DizimistaInline(admin.TabularInline):
    model = Dizimista
    view_on_site = True
    fields = []


@admin.register(Igreja)
class IgrejaAdmin(admin.ModelAdmin, ExportPdfMixin):
    list_display = (
        "nome",
        "endereco",
        "agentes_da_pastoral",
        "gestores_da_patoral",
        "número_de_dizimistas",
    )
    sortable_by = list_display
    search_fields = ["nome"]
    actions = ["export_as_pdf"]
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
            display_text.append(str(user.perfil or user))
        return ", ".join(display_text)

    def agentes_da_pastoral(self, obj: Igreja):
        display_text = []
        for user in obj.agentes.all():
            display_text.append(str(user.perfil or user))
        return ", ".join(display_text)


class RegistradoPorListFilter(admin.SimpleListFilter):
    title = _("Registrado Por")
    parameter_name = "registrado_por"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin):  # noqa
        registradores = set(
            p.registrado_por for p in model_admin.get_queryset(request).all()
        )
        return [(r.id, r.perfil) for r in registradores if r]

    def queryset(self, request: HttpRequest, queryset):
        if self.value():
            return queryset.filter(registrado_por__pk=self.value())
        return queryset


class PagamentoIgrejaFilter(IgrejaListFilter):
    field = "dizimista__igreja__pk"


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin, ExportPdfMixin):
    fields = ("dizimista", "valor", "data", "registrado_por", "id")
    list_per_page = 20
    list_display = ["data", "valor", "dizimista_link"]
    sortable_by = list_display
    list_select_related = True
    autocomplete_fields = ["dizimista"]
    search_fields = ["dizimista__perfil__nome"]
    list_filter = [
        PagamentoIgrejaFilter,
        "data",
        DataMonthListFilter,
        RegistradoPorListFilter,
    ]
    actions = ["export_as_pdf"]

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        # if request.user.is_superuser:
        #     return []
        return ["data", "registrado_por", "id"]

    def save_model(self, request: HttpRequest, obj, form, change):
        obj.registrado_por = request.user
        super().save_model(request, obj, form, change)
        try:
            destinatários = []
            if obj.dizimista.email:
                destinatários.append(obj.dizimista.email)
            send_mail(
                subject="Registro de pagamento",
                message="",
                html_message=render_to_string("pagamento.html/", dict(obj=obj)),
                from_email=EMAIL_HOST_USER,
                recipient_list=destinatários,
                fail_silently=False,
            )
            self.message_user(request, "E-mails enviados com sucesso.", level="success")
        except Exception as e:
            print(e)
            self.message_user(request, "Erro ao enviar e-mail", level="warning")

    def dizimista_link(self, obj):
        try:
            return obj.dizimista.link()
        except Exception as exc:
            print(exc)
            return ""

    dizimista_link.short_description = "Dizimista"

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        igrejas = igrejas_do_usuário(user)
        return qs.filter(dizimista__igreja__in=igrejas)


def group_date_by_periord(queryset, period):
    groups_settings = {
        "dia": dict(field="day", func=TruncDay, date_format="%Y-%m-%d"),
        "semana": dict(field="week", func=TruncWeek, date_format="%Y-%m-%d"),
        "mês": dict(field="month", func=TruncMonth, date_format="%Y-%m"),
        "ano": dict(field="year", func=TruncYear, date_format="%Y"),
    }
    gs = groups_settings[period]
    truncate_function = gs["func"]
    queryset = (
        queryset.annotate(**{period: truncate_function("data")})
        .order_by(f"-{period}")
        .values(period, "dizimista__igreja__nome")
    ).annotate(pagamentos=Count("id"), total_recebido=Sum("valor"))
    date_format = groups_settings[period]["date_format"]
    for row in queryset:
        row[period] = row[period].strftime(date_format)
    return queryset


class GroupByDateListFilter(admin.SimpleListFilter):
    title = _("Agrupar por")
    parameter_name = "group_date_by"
    groups_settings = {
        "dia": dict(field="day", func=TruncDay, date_format="%Y-%m-%d"),
        "semana": dict(field="week", func=TruncWeek, date_format="%Y-%m-%d"),
        "mês": dict(field="month", func=TruncMonth, date_format="%Y-%m"),
        "ano": dict(field="year", func=TruncYear, date_format="%Y"),
    }
    selected_group = "mês"

    def lookups(self, request: HttpRequest, model_admin):  # noqa
        return [(_.lower(), _) for _ in ["Dia", "Semana", "Mês", "Ano"]]

    def queryset(self, request: HttpRequest, queryset):
        GroupByDateListFilter.selected_group = self.value() or "mês"
        return queryset


def format_plot_data(queryset, period):
    reversed_qs = sorted(queryset, key=lambda x: x[period])
    igrejas = set(_["dizimista__igreja__nome"] for _ in queryset)
    plot_data = [
        dict(
            x=[_[period] for _ in reversed_qs if _["dizimista__igreja__nome"] == i],
            y=[
                float(_["total_recebido"])
                for _ in reversed_qs
                if _["dizimista__igreja__nome"] == i
            ],
            type="bar",
            name=i,
        )
        for i in igrejas
    ]
    return plot_data


@admin.register(ResumoPagamentos)
class ResumoPagamentosAdmin(admin.ModelAdmin, GroupByDateListFilter):
    change_list_template = "admin/resumopagamentos/change_list.html"
    list_filter = (PagamentoIgrejaFilter, GroupByDateListFilter, DataMonthListFilter)

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        igrejas = igrejas_do_usuário(user)
        return qs.filter(dizimista__igreja__in=igrejas)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            queryset = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response
        if queryset:
            period = self.selected_group
            print(period)
            date_format = self.groups_settings[period]["date_format"]
            queryset = group_date_by_periord(queryset, period)
            plot_data = format_plot_data(queryset, period)
            response.context_data["plot_data"] = plot_data
            response.context_data["xaxis"] = dict(
                title=period.title(), tickformat=date_format
            )
            response.context_data["yaxis"] = dict(title="Total Recebido (R$)")
            response.context_data["plot_id"] = "chart"
            response.context_data["data"] = queryset
            response.context_data["headers"] = [
                "Igreja",
                self.selected_group.title(),
                "Pagamentos",
                "Total (R$)",
            ]
        return response
