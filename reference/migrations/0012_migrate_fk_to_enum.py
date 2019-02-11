# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-04 03:40
from __future__ import unicode_literals

from django.db import migrations

from reference.migrations.utils.enum import move_fk_to_enum


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0011_add_field_gtype_to_enum'),
    ]

    operations = [
        migrations.RunPython(move_fk_to_enum),
        migrations.RemoveField(
            model_name='gradetype',
            name='institutional_grade_type',
        ),
        migrations.RenameField(
            model_name='gradetype',
            old_name='institutional_grade_type_enum',
            new_name='institutional_grade_type'
        ),
        migrations.DeleteModel(
            name='InstitutionalGradeType',
        ),
    ]
