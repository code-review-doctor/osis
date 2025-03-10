# Generated by Django 2.2.24 on 2021-12-03 09:37
from django.db import migrations
from django.db.models import Prefetch


def correct_entity_main_address(apps, schema_editor):
    entity_version_model = apps.get_model('base', 'EntityVersion')
    entity_version_address = apps.get_model('base', 'EntityVersionAddress')

    entity_versions = entity_version_model.objects.only_roots().prefetch_related(
        Prefetch(
            'entityversionaddress_set',
            queryset=entity_version_address.objects.all().select_related('country')
        )
    )
    for obj in entity_versions:
        if len(obj.entityversionaddress_set.all()) == 1:
            entity_version_address = obj.entityversionaddress_set.all()[0]
            entity_version_address.is_main = True
            entity_version_address.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0616_auto_20211116_1317'),
    ]

    operations = [
        migrations.RunPython(correct_entity_main_address, elidable=True),
    ]
