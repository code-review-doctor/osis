# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-05-21 15:41
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0458_auto_20190613_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningcontaineryear',
            name='additional_entity_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='additional_entities_1', to='base.Entity'),
        ),
        migrations.AddField(
            model_name='learningcontaineryear',
            name='additional_entity_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='additional_entities_2', to='base.Entity'),
        ),
        migrations.AddField(
            model_name='learningcontaineryear',
            name='allocation_entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='allocation_entities', to='base.Entity'),
        ),
        migrations.AddField(
            model_name='learningcontaineryear',
            name='requirement_entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='requirement_entities', to='base.Entity'),
        ),
    ]
