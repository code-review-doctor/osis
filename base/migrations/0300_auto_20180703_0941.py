# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-07-03 07:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0299_remove_learningunityear_bibliography'),
    ]

    operations = [
        # Remove all teaching material because this table will implement OrderedModel
        migrations.RunSQL("DELETE FROM base_teachingmaterial;", elidable=True),
        migrations.AddField(
            model_name='teachingmaterial',
            name='order',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
            preserve_default=False,
        )
    ]
