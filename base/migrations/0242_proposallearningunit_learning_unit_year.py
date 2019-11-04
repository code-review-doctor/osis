# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-03-16 12:11
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0241_remove_proposallearningunit_learning_unit_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposallearningunit',
            name='learning_unit_year',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='base.LearningUnitYear'),
            preserve_default=False,
        ),
    ]
