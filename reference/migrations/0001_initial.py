# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-21 22:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Continent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=2, unique=True)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iso_code', models.CharField(max_length=2, unique=True)),
                ('name', models.CharField(max_length=80, unique=True)),
                ('nationality', models.CharField(blank=True, max_length=80, null=True)),
                ('european_union', models.BooleanField(default=False)),
                ('dialing_code', models.CharField(blank=True, max_length=3, null=True)),
                ('cref_code', models.CharField(blank=True, max_length=3, null=True)),
                ('continent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Continent')),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True)),
                ('code', models.CharField(blank=True, max_length=4, null=True)),
                ('symbol', models.CharField(blank=True, max_length=6, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=4, unique=True)),
                ('name', models.CharField(max_length=80, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='country',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.Currency'),
        ),
    ]
