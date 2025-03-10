# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-14 12:38
from __future__ import unicode_literals

from django.db import migrations


def _find_learning_unit_component(learning_unit_component):
    return learning_unit_component.objects.filter(learning_component_year__isnull=True)


def delete_learning_unit_component(apps, schema_editor):
    learning_unit_component = apps.get_model('base', 'learningunitcomponent')
    learning_unit_components = _find_learning_unit_component(learning_unit_component)
    for learning_unit_component in learning_unit_components:
        learning_unit_component.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0157_entitymanager_entity'),
    ]

    operations = [
        migrations.RunPython(delete_learning_unit_component, elidable=True),
    ]
