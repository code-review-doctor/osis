# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-29 12:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0027_auto_20180117_1322'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attributionnew',
            unique_together=set([('learning_container_year', 'tutor', 'function', 'deleted')]),
        ),
        migrations.AlterUniqueTogether(
            name='tutorapplication',
            unique_together=set([('learning_container_year', 'tutor', 'function', 'deleted')]),
        ),
    ]
