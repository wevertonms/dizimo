from faker import Faker
from random import choice
from gestao.models import Dizimista, Igreja, Pagamento
from django.contrib.auth.models import User
from django.utils import timezone

FAKER = Faker("pt-BR")

USERS = User.objects.filter(is_superuser=False)
IGREJAS = Igreja.objects.all()
PAGAMENTOS_VALORES = (20, 30, 40, 50, 70, 100, 200)


def get_endereco():
    return FAKER.address().split("\n")[0]


def add_pagamentos(dizimista, from_last_n_months, to_n_last_month):
    for m in range(from_last_n_months, to_n_last_month, -1):
        p = Pagamento(
            dizimista=dizimista,
            igreja=dizimista.igreja,
            data=timezone.make_aware(FAKER.date_time_between(f"-{m}M", f"-{m-1}M")),
            valor=choice(PAGAMENTOS_VALORES),
            registrado_por=choice(USERS),
        )
        p.save()


def get_dizimista(igrejas=IGREJAS):
    profile = FAKER.simple_profile()
    dados = dict(
        nome=profile["name"],
        genero=profile["sex"],
        endereco=get_endereco(),
        nascimento=FAKER.date_between("-70y", "-20y"),
        telefone=FAKER.phone_number(),
        email=profile["mail"],
        igreja=choice(igrejas),
    )
    return Dizimista(**dados)


def adicionar_dizimistas_e_pagamentos(
    number_dizimistas=10, igrejas=IGREJAS, from_last_n_months=4, to_n_last_month=0
):
    for _ in range(number_dizimistas):
        d = get_dizimista(igrejas)
        d.save()
        add_pagamentos(d, from_last_n_months, to_n_last_month)


def add_igreja(nome):
    Igreja.objects.create(nome=nome, endereco=get_endereco())