# Generated by Django 5.2.1 on 2025-05-22 17:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Estagiario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefone', models.CharField(max_length=20)),
                ('data_inicio', models.DateField()),
                ('ativo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Presenca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('entrada', models.TimeField()),
                ('saida', models.TimeField(blank=True, null=True)),
                ('horas', models.CharField(blank=True, max_length=10, null=True)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('estagiario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.estagiario')),
            ],
        ),
    ]
