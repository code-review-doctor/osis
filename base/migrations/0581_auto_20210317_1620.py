# Generated by Django 2.2.13 on 2021-03-17 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0580_merge_20210317_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academiccalendar',
            name='title',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
