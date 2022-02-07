# Generated by Django 2.2.24 on 2022-02-02 11:32

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('reference', '0011_auto_20220131_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='highschool',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
