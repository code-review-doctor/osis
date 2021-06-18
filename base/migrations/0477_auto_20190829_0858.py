# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-08-29 08:58
from __future__ import unicode_literals

from django.db import migrations


def start_years(apps, schema_editor):
    learning_unit_model = apps.get_model('base', 'learningunit')
    learning_units = learning_unit_model.objects.all()
    academic_year_model = apps.get_model('base', 'academicyear')
    academic_years = academic_year_model.objects.all().values('pk', 'year')
    for learning_unit in learning_units:
        academic_year_id = list(filter(lambda item: item['year'] == learning_unit.start_year, academic_years))
        if academic_year_id:
            learning_unit.new_start_year_id = academic_year_id[0]['pk']
            learning_unit.save()
        academic_year_id = list(filter(lambda item: item['year'] == learning_unit.end_year, academic_years))
        if academic_year_id:
            learning_unit.new_end_year_id = academic_year_id[0]['pk']
            learning_unit.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0476_auto_20190829_0856'),
    ]

    operations = [
        migrations.RunPython(start_years, reverse_code=migrations.RunPython.noop, elidable=True),
    ]
