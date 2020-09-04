from gestao.admin import endereco
from faker import Faker
from random import choice
from gestao.models import Dizimista, Igreja, Pagamento
from django.contrib.auth.models import User

faker = Faker("pt-BR")

USERS = User.objects.filter(is_superuser=False)
IGREJAS = Igreja.objects.all()
PAGAMENTOS_VALORES = (20, 30, 40, 50, 70, 100, 200)


def get_endereco():
    return faker.address().split("\n")[0]


def add_pagamentos(dizimista, from_last_n_months, to_n_last_month):
    for m in range(from_last_n_months, to_n_last_month, -1):
        p = Pagamento(
            dizimista=dizimista,
            igreja=dizimista.igreja,
            data=faker.date_time_between(f"-{m}M", f"-{m-1}M"),
            valor=choice(PAGAMENTOS_VALORES),
            registrado_por=choice(USERS),
        )
        p.save()


def get_dizimista(igrejas=IGREJAS):
    p = faker.simple_profile()
    dados = dict(
        nome=p["name"],
        genero=p["sex"],
        endereco=get_endereco(),
        nascimento=faker.date_between("-70y", "-20y"),
        telefone=faker.phone_number(),
        email=p["mail"],
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