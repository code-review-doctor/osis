# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-04-23 18:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0447_auto_20190405_1518'),
    ]

    operations = [
        migrations.RunSQL(
            """
                DELETE from base_entitycomponentyear
                USING base_learningcomponentyear 
                 where base_learningcomponentyear.id = base_entitycomponentyear.learning_component_year_id
                 and base_learningcomponentyear.learning_unit_year_id is null
            """,
            elidable=True
        ),
        migrations.RunSQL(
            """
                DELETE from base_learningclassyear
                USING base_learningcomponentyear 
                 where base_learningcomponentyear.id = base_learningclassyear.learning_component_year_id
                 and base_learningcomponentyear.learning_unit_year_id is null
            """,
            elidable=True
        ),
        migrations.RunSQL(
            """
                DELETE from base_learningcomponentyear where learning_unit_year_id is null
            """,
            elidable=True
        ),
    ]
