from django import template
from django.db.models import Sum
from django.utils.timezone import now

from gestao.admin import (
    dizimistas_do_usuário,
    format_plot_data,
    group_date_by_periord,
    igrejas_do_usuário,
)
from gestao.models import Pagamento

register = template.Library()


def pagamentos(user):
    igrejas = igrejas_do_usuário(user)
    if user.is_superuser:
        user_filter = {}
    else:
        user_filter = dict(dizimista__igreja__in=igrejas)
    return Pagamento.objects.filter(data__month__gte=now().month, **user_filter)


@register.simple_tag(takes_context=True)
def plot(context):
    queryset = pagamentos(context["user"])
    period = "semana"
    queryset = group_date_by_periord(queryset, period)
    plot_data = format_plot_data(queryset, period)
    context["plot_data"] = plot_data
    context["xaxis"] = dict(title=period.title(), tickformat="%Y-%m-%d")
    context["yaxis"] = dict(title="Total Recebido (R$)")
    context["plot_id"] = "chart"
    return ""


@register.simple_tag(takes_context=True)
def num_pagamentos_este_mes(context):
    return pagamentos(context["user"]).count()


@register.simple_tag(takes_context=True)
def num_dizimistas(context):
    return dizimistas_do_usuário(user=context["user"]).count()


@register.simple_tag(takes_context=True)
def recebido_este_mes(context):
    return pagamentos(context["user"]).aggregate(total=Sum("valor"))["total"]
