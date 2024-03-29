# Generated by Django 3.1.1 on 2020-09-06 20:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gestao", "0004_auto_20200905_1654"),
    ]

    operations = [
        migrations.AlterField(
            model_name="igreja",
            name="agentes",
            field=models.ManyToManyField(
                related_name="agente_em", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="igreja",
            name="coordenadores",
            field=models.ManyToManyField(
                related_name="coordenador_em", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
