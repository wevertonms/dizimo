from random import choice, random

from django.utils import timezone
from faker import Faker

from core.models import Perfil
from gestao.admin import AGENTES_GROUP, GESTORES_GROUP
from gestao.models import Dizimista, Igreja, Pagamento, PerfilDizimista, User

FAKER = Faker("pt-BR")
TAXA_DE_INADIMPLENCIA = 0.9
PAGAMENTOS_VALORES = (20, 30, 40, 50, 70, 100, 200)


def all_users():
    return User.objects.filter(is_superuser=False)


def all_igrejas():
    return Igreja.objects.all()


def get_endereco():
    return FAKER.address().split("\n")[0]


def profile_data():
    profile = FAKER.simple_profile()
    return dict(
        nome=profile["name"].split(".")[-1].strip(),
        genero=profile["sex"],
        endereco=get_endereco(),
        nascimento=FAKER.date_between("-70y", "-20y"),
        telefone=FAKER.phone_number(),
        email=profile["mail"],
    )


def add_pagamentos(dizimista, from_last_n_months, to_n_last_month):
    for m in range(from_last_n_months, to_n_last_month, -1):
        if random() < TAXA_DE_INADIMPLENCIA:
            igreja = dizimista.igreja  # type: Igreja
            p = Pagamento(
                dizimista=dizimista,
                data=timezone.make_aware(FAKER.date_time_between(f"-{m}M", f"-{m-1}M")),
                valor=choice(PAGAMENTOS_VALORES),
                registrado_por=choice(igreja.agentes.all()),
            )
            p.save()


def get_dizimista(igrejas=None):
    igrejas = igrejas or all_igrejas()
    igreja = choice(igrejas)
    dizimo = choice(PAGAMENTOS_VALORES)
    dizimista = Dizimista.objects.create(igreja=igreja, dizimo=dizimo)
    PerfilDizimista.objects.create(
        **profile_data(),
        dizimista=dizimista,
    )
    return dizimista


def adicionar_dizimistas_e_pagamentos(
    number_dizimistas=40, igrejas=None, from_last_n_months=4, to_n_last_month=0
):
    print("Adicionando pagamentos...")
    igrejas = igrejas or all_igrejas()
    for _ in range(number_dizimistas):
        d = get_dizimista(igrejas)
        d.save()
        add_pagamentos(d, from_last_n_months, to_n_last_month)
    print("Pagamentos adicionados!")


def create_teste_user():
    teste = User.objects.create_user(
        username="teste",
        password="teste",
        is_staff=True,
    )  # type: User
    Perfil.objects.create(user=teste, **profile_data())
    teste.groups.add(GESTORES_GROUP())
    teste.save()


def adicionar_igrejas(num_igrejas=3, gestores_por_igreja=1, agentes_por_igreja=2):
    for i in range(num_igrejas):
        igreja = Igreja.objects.create(
            nome=f"Igreja {i}", endereco=get_endereco()
        )  # type: Igreja
        print(f"{igreja} adicionada...")
        for j in range(1, agentes_por_igreja + 1):
            agente = User.objects.create_user(
                username=f"agente{i*agentes_por_igreja + j}",
                password=f"agente{i*agentes_por_igreja + j}",
                is_staff=True,
            )  # type: User
            Perfil.objects.create(user=agente, **profile_data())
            agente.groups.add(AGENTES_GROUP())
            agente.save()
            igreja.agentes.add(agente)
            print(f"Agente {(agente)} adicionado...")
        for j in range(1, gestores_por_igreja + 1):
            gestor = User.objects.create_user(
                username=f"gestor{i*gestores_por_igreja + j}",
                password=f"gestor{i*gestores_por_igreja + j}",
                is_staff=True,
            )  # type: User
            Perfil.objects.create(user=gestor, **profile_data())
            gestor.groups.add(GESTORES_GROUP())
            gestor.save()
            igreja.gestores.add(gestor)
            print(f"Gestor {(gestor)} adicionado...")
        igreja.save()


def populate_full(num_igrejas=3, num_dizimistas=100):
    adicionar_igrejas(num_igrejas)
    adicionar_dizimistas_e_pagamentos(num_dizimistas)


def delete_all():
    print(Igreja.objects.all().delete())
    print(Dizimista.objects.all().delete())
    print(Pagamento.objects.all().delete())
    print(PerfilDizimista.objects.all().delete())
    print(Perfil.objects.all().delete())
    print(User.objects.exclude(username="admin").delete())
