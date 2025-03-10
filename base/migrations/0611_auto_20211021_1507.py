# Generated by Django 2.2.13 on 2021-10-21 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0610_remove_learningunityear_decimal_scores'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='birth_place',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='first_name_in_use',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='person',
            name='id_card_number',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='national_number',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='passport_expiration_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='passport_number',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
