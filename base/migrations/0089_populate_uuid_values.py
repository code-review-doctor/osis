# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-05 09:13
from __future__ import unicode_literals

from django.db import migrations

from base.migrations.utils import utils


def set_uuid_field(apps, schema_editor):
    utils.set_uuids_model(apps, "learningunit")


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0088_auto_20170106_1728'),
    ]

    operations = [
        migrations.RunPython(set_uuid_field, elidable=True),
    ]
