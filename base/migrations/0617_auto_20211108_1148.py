# Generated by Django 2.2.13 on 2021-11-08 11:48

import django.core.validators
from django.db import migrations, models
import osis_document.contrib.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0616_auto_20211105_1315'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningcontaineryear',
            name='uuid',
        ),
        migrations.RemoveField(
            model_name='learningunit',
            name='uuid',
        ),
    ]
