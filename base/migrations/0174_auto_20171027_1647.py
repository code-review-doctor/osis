# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-27 14:47
from __future__ import unicode_literals

from django.db import migrations

from base.migrations.utils import utils


def set_uuid_field(apps, schema_editor):
    utils.set_uuids_model(apps, "learningcontaineryear")
    utils.set_uuids_model(apps, "learningcomponentyear")


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0173_auto_20171027_1646'),
    ]

    operations = [
        migrations.RunPython(set_uuid_field, elidable=True),
    ]
