# Generated by Django 3.1.1 on 2020-09-08 04:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0008_auto_20200908_0005'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ResumoPagamentos',
        ),
        migrations.CreateModel(
            name='ResumoDiarios',
            fields=[
            ],
            options={
                'verbose_name': 'Resumo de Pagamentos',
                'verbose_name_plural': 'Resumos de Pagamentos',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('gestao.pagamento',),
        ),
    ]