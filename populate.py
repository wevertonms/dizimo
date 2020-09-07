from faker import Faker
from random import choice

from gestao.models import Dizimista, Igreja, Pagamento, User
from gestao.admin import GESTORES_GROUP, AGENTES_GROUP
from django.utils import timezone

FAKER = Faker("pt-BR")

PAGAMENTOS_VALORES = (20, 30, 40, 50, 70, 100, 200)


def all_users():
    return User.objects.filter(is_superuser=False)


def all_igrejas():
    return Igreja.objects.all()


def get_endereco():
    return FAKER.address().split("\n")[0]


def add_pagamentos(dizimista, from_last_n_months, to_n_last_month):
    for m in range(from_last_n_months, to_n_last_month, -1):
        igreja = dizimista.igreja  # type: Igreja
        p = Pagamento(
            dizimista=dizimista,
            igreja=igreja,
            data=timezone.make_aware(FAKER.date_time_between(f"-{m}M", f"-{m-1}M")),
            valor=choice(PAGAMENTOS_VALORES),
            registrado_por=choice(igreja.agentes.all()),
        )
        p.save()


def get_dizimista(igrejas=None):
    igrejas = igrejas or all_igrejas()
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
    number_dizimistas=40, igrejas=None, from_last_n_months=4, to_n_last_month=0
):
    igrejas = igrejas or all_igrejas()
    for _ in range(number_dizimistas):
        d = get_dizimista(igrejas)
        d.save()
        add_pagamentos(d, from_last_n_months, to_n_last_month)


def adicionar_igrejas(num_igrejas=1, gestores_por_igreja=1, agentes_por_igreja=2):
    for i in range(1, num_igrejas + 1):
        igreja = Igreja.objects.create(
            nome=f"Igreja {i}", endereco=get_endereco()
        )  # type: Igreja
        print(f"{igreja} adicionada...")
        for j in range(agentes_por_igreja):
            agente = User.objects.create_user(
                username=f"agente{i*agentes_por_igreja + j}",
                password=f"agente{i*agentes_por_igreja + j}",
                is_staff=True,
                first_name=FAKER.first_name(),
            )  # type: User
            agente.groups.add(AGENTES_GROUP())
            agente.save()
            igreja.agentes.add(agente)
            print(f"Agente {(agente)} adicionado...")
        for j in range(gestores_por_igreja):
            gestor = User.objects.create_user(
                username=f"gestor{i*gestores_por_igreja + j}",
                password=f"gestor{i*gestores_por_igreja + j}",
                is_staff=True,
                first_name=FAKER.first_name(),
            )  # type: User
            gestor.groups.add(GESTORES_GROUP())
            gestor.save()
            igreja.gestores.add(gestor)
            print(f"Gestor {(gestor)} adicionado...")
        igreja.save()


def pupulate_full(num_igrejas=2, num_dizimistas=100):
    adicionar_igrejas(num_igrejas)
    adicionar_dizimistas_e_pagamentos(num_dizimistas)