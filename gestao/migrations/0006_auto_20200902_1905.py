# Generated by Django 3.1.1 on 2020-09-02 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0005_auto_20200902_1818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dizimista',
            name='telefone',
            field=models.CharField(max_length=17, null=True, verbose_name='Telefone'),
        ),
    ]
