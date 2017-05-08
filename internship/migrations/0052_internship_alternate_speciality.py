# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-07 12:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0051_auto_20170503_0045'),
    ]

    operations = [
        migrations.AddField(
            model_name='internship',
            name='alternate_speciality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alternate_speciality', to='internship.InternshipSpeciality'),
        ),
    ]
