# Generated by Django 2.2.13 on 2020-10-29 15:50

from django.db import migrations


def forward(apps, schema_editor):
    EntityVersionAddress = apps.get_model('base', 'EntityVersionAddress')
    EntityVersionAddress.objects.filter(city="LEUVEN").update(city="Leuven")


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0541_auto_20201019_1604'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OrganizationAddress',
        ),
        migrations.RunPython(forward, migrations.RunPython.noop)
    ]
