# Generated by Django 3.1.1 on 2020-09-14 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_perfil_dizimista'),
        ('gestao', '0019_dizimista_perfil'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerfilDizimista',
            fields=[
                ('perfil_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.perfil')),
            ],
            bases=('core.perfil',),
        ),
        migrations.AlterField(
            model_name='dizimista',
            name='perfil',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gestao.perfildizimista'),
        ),
    ]
