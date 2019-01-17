# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-01-16 14:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0424_auto_20190116_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationgroupyear',
            name='funding_direction',
            field=models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], default='', max_length=1, verbose_name='Funding direction'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='funding_direction_cud',
            field=models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], default='', max_length=1, verbose_name='Funding international cooperation CCD/CUD direction'),
        ),
    ]
