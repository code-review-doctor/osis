# Generated by Django 2.2.13 on 2021-06-23 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0587_auto_20210603_1411'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningcomponentyear',
            name='uuid',
        ),
    ]
