# Generated by Django 2.2.13 on 2021-06-14 12:47

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('attribution', '0001_squashed_0045_auto_20210318_0949'),
    ]

    operations = [
        migrations.AddField(
            model_name='attributionnew',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
