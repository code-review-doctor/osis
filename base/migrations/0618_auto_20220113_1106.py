# Generated by Django 2.2.24 on 2022-01-13 11:06

from django.db import migrations
from django.db.models import Exists, OuterRef


def delete_tutors_without_attribution(apps, schema_editor):
    Tutor = apps.get_model('base', 'Tutor')
    AttributionNew = apps.get_model('attribution', 'AttributionNew')
    Group = apps.get_model('auth', 'Group')
    problematic_tutors = Tutor.objects.annotate(
        has_attribution=Exists(
            queryset=AttributionNew.objects.filter(
                tutor_id=OuterRef('pk')
            )
        )
    ).filter(
        has_attribution=False
    )
    print("{} problematic tutors (without attributions)".format(len(problematic_tutors)))
    group = Group.objects.get(name='tutors')
    for tutor in problematic_tutors:
        user = tutor.person.user
        if user:
            print("Removing {} from tutors group".format(tutor))
            user.groups.remove(group)
    problematic_tutors.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0617_entity_address_is_main_correction'),
    ]

    operations = [
        migrations.RunPython(delete_tutors_without_attribution)
    ]
