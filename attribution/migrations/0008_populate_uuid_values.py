# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-05 09:13
from __future__ import unicode_literals
from django.core.exceptions import FieldDoesNotExist
from django.db import migrations
import uuid


def set_uuid_field(apps, schema_editor):
    attribution = apps.get_app_config('attribution')
    for model_class in attribution.get_models():
        ids = model_class.objects.values_list('id', flat=True)
        if ids:
            for pk in ids:
                try:
                    model_class.objects.filter(pk=pk).update(uuid=uuid.uuid4())
                except FieldDoesNotExist:
                    break


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0007_attribution_uuid'),
    ]

    operations = [
        migrations.RunPython(set_uuid_field),
    ]
