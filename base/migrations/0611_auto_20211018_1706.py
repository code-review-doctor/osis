# Generated by Django 2.2.13 on 2021-10-18 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0610_remove_learningunityear_decimal_scores'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessionexam',
            name='education_group_year',
        ),
        migrations.RemoveField(
            model_name='sessionexam',
            name='learning_unit_year',
        ),
    ]
