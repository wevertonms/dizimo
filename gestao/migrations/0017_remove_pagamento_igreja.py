# Generated by Django 3.1.1 on 2020-09-13 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gestao", "0016_remove_dizimista_perfil"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pagamento",
            name="igreja",
        ),
    ]
