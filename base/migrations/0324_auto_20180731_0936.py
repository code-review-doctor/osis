# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-07-31 07:36
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0323_auto_20180730_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationgroupyear',
            name='management_entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='management_entity', to='base.Entity', verbose_name='management_entity'),
        ),
    ]
