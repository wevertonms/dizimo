# Generated by Django 3.1.1 on 2020-09-13 19:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestao", "0016_remove_dizimista_perfil"),
        ("core", "0002_auto_20200913_1022"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfil",
            name="dizimista",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="gestao.dizimista",
            ),
        ),
    ]
