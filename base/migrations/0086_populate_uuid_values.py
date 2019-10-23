# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-05 09:13
from __future__ import unicode_literals

from django.db import migrations

from base.migrations.utils import utils


def set_uuid_field(apps, schema_editor):
    utils.set_uuids_model(apps, "learningunitcomponent")
    utils.set_uuids_model(apps, "learningunitenrollment")
    utils.set_uuids_model(apps, "learningunityear")


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0085_auto_20170105_1315'),
    ]

    operations = [
        migrations.RunPython(set_uuid_field),
    ]
