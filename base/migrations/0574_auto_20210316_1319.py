# Generated by Django 2.2.13 on 2021-03-16 13:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0573_auto_20210305_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentspecificprofile',
            name='arrangement_comment',
            field=models.CharField(blank=True, max_length=2000, null=True,
                                   verbose_name='Details other educational facilities'),
        ),
    ]
