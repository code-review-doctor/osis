# Generated by Django 2.2.24 on 2022-01-12 11:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('attribution', '0014_merge_20220106_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorapplication',
            name='volume_lecturing',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='tutorapplication',
            name='volume_pratical_exercice',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]
