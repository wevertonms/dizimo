# Generated by Django 3.1.1 on 2020-09-13 19:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200913_1022'),
        ('gestao', '0014_auto_20200913_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dizimista',
            name='perfil',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.perfil', verbose_name='Perfil'),
        ),
    ]
