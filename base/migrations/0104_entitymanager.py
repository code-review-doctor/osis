# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-20 06:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0103_auto_20170419_1030'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntityManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Person')),
                ('structure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Structure')),
            ],
            options={
                'permissions': (('is_entity_manager', 'Is entity manager '),),
            },
        ),

        migrations.AddField(
            model_name='person',
            name='employee',
            field=models.BooleanField(default=False),
        ),
    ]
