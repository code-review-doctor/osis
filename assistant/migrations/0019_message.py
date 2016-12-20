# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-20 09:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0081_auto_20161207_1432'),
        ('assistant', '0018_auto_20160812_0920'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('type', models.CharField(choices=[('TO_ALL_ASSISTANTS', 'To_all_assistants'), ('TO_ALL_DEANS', 'To_All_Deans'), ('TO_PHD_SUPERVISOR', 'To_Phd_Supervisor'), ('TO_ONE_DEAN', 'To_One_Dean')], max_length=20)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.AcademicYear')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistant.Manager')),
            ],
        ),
    ]
