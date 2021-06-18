# Generated by Django 2.2.13 on 2021-06-03 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0586_auto_20210510_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admissionconditionline',
            name='access',
            field=models.CharField(choices=[('-', '-'), ('direct_access', 'Direct Access'), ('on_the_file', 'Access based on application'), ('access_with_training', 'Access with additional training')], default='-', max_length=32),
        ),
    ]
