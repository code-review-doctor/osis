# Generated by Django 2.2.13 on 2020-10-12 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0539_auto_20201006_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entityversionaddress',
            name='city',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='entityversionaddress',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reference.Country'),
        ),
    ]
