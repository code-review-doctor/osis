# Generated by Django 2.2.13 on 2021-08-20 08:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0004_auto_20210819_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoresheetaddress',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.Entity', verbose_name='Entity of reference'),
        ),
    ]
