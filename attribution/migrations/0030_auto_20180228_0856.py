# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-28 07:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0029_WARNING_INDEX_20180129_1441'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attributionnew',
            unique_together=set([]),
        ),
        migrations.RunSQL(
            "DROP INDEX attributionnew_learningcontaineryearid_tutorid_function_deleted",
            """CREATE UNIQUE INDEX attributionnew_learningcontaineryearid_tutorid_function_deleted
                    ON attribution_attributionnew
                (learning_container_year_id, tutor_id, function, coalesce(deleted,'2000-01-01'));""",
            elidable=True
        ),
    ]
