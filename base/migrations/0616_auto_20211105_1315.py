# Generated by Django 2.2.13 on 2021-11-05 13:15

import django.core.validators
from django.db import migrations, models
import osis_document.contrib.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0615_auto_20211026_1027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningunityear',
            name='uuid',
        ),
    ]
