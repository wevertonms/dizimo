# Generated by Django 3.1.1 on 2020-09-02 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0002_auto_20200902_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='dizimista',
            name='telefone',
            field=models.CharField(max_length=14, null=True, verbose_name='Telefone'),
        ),
    ]
