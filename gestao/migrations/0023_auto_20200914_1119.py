# Generated by Django 3.1.1 on 2020-09-14 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestao', '0022_auto_20200914_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfildizimista',
            name='dizimista',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='perfil', to='gestao.dizimista'),
        ),
    ]
