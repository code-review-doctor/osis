# Generated by Django 2.2.24 on 2022-01-19 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0009_auto_20211025_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='dialing_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
