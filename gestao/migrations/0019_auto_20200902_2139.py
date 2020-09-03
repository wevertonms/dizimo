# Generated by Django 3.1.1 on 2020-09-02 21:39

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0018_auto_20200902_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dizimista',
            name='genero',
            field=models.CharField(choices=[('F', 'Feminino'), ('M', 'Masculino'), ('O', 'Outro')], default='F', max_length=1),
        ),
        migrations.AlterField(
            model_name='pagamento',
            name='data',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 2, 21, 39, 1, 999182, tzinfo=utc), verbose_name='Data e hora'),
        ),
    ]
