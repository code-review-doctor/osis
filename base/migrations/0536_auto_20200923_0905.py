# Generated by Django 2.2.13 on 2020-09-23 09:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0535_auto_20200908_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningunityear',
            name='professional_integration',
            field=models.BooleanField(default=False, verbose_name='Professional integration'),
        ),
    ]
