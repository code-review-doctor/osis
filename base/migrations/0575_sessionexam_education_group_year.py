# Generated by Django 2.2.13 on 2021-01-27 17:04
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0574_auto_20210311_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionexam',
            name='education_group_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupYear'),
        ),
    ]
