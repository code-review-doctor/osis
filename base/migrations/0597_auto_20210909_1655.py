# Generated by Django 2.2.13 on 2021-09-09 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0596_auto_20210909_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='external_id',
            field=models.CharField(blank=True, db_index=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='person',
            name='first_name',
            field=models.CharField(blank=True, db_index=True, default='', max_length=50),
        ),
    ]
