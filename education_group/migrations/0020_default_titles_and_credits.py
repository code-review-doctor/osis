from django.db import migrations
from django.utils import timezone

from base.models.enums.education_group_types import GroupType
from base.models.group_element_year import GroupElementYear
from education_group.models.group_year import GroupYear


def add_default_credits_to_minor_list_choices(apps, schema_editor):
    geys = GroupElementYear.objects.filter(
        parent_element__group_year__academic_year__year__gt=2019,
        parent_element__group_year__education_group_type__name=GroupType.MINOR_LIST_CHOICE.name,
        child_element__isnull=False
    ).exclude(
        parent_element__group_year__credits=30
    )
    minor_list_choices = []
    for gey in geys:
        group_year = gey.parent_element.group_year
        group_year.credits = 30
        group_year.changed = timezone.now()
        minor_list_choices.append(group_year)
    GroupYear.objects.bulk_update(minor_list_choices, ['credits', 'changed'], batch_size=1000)


def add_default_titles_to_minor_option_list_choice_and_complementary_module(apps, schema_editor):
    groups = GroupYear.objects.filter(
        academic_year__year__gt=2019,
        education_group_type__name__in=[
            GroupType.COMPLEMENTARY_MODULE.name,
            GroupType.MINOR_LIST_CHOICE.name,
            GroupType.OPTION_LIST_CHOICE.name
        ]
    )
    minor_list_choices = groups.filter(education_group_type__name=GroupType.MINOR_LIST_CHOICE.name)
    for mlc in minor_list_choices:
        mlc.title_fr = 'Mineure ou approfondissement'
        mlc.title_en = 'Minor or additional module'
        mlc.changed = timezone.now()
    option_list_choices = groups.filter(education_group_type__name=GroupType.OPTION_LIST_CHOICE.name)
    for olc in option_list_choices:
        olc.title_fr = 'Liste des options'
        olc.title_en = 'List of electives'
        olc.changed = timezone.now()
    complementary_modules = groups.filter(education_group_type__name=GroupType.COMPLEMENTARY_MODULE.name)
    for cm in complementary_modules:
        cm.title_fr = 'Enseignements supplémentaires (module complémentaire) au master'
        cm.title_en = 'Additional courses (preparatory module) to the master'
        cm.changed = timezone.now()
    GroupYear.objects.bulk_update(
        list(minor_list_choices) + list(option_list_choices) + list(complementary_modules),
        ['title_fr', 'title_en', 'changed'],
        batch_size=1000
    )


class Migration(migrations.Migration):
    dependencies = [
        ('education_group', '0019_auto_20210203_1310'),
    ]

    operations = [
        migrations.RunPython(add_default_credits_to_minor_list_choices),
        migrations.RunPython(add_default_titles_to_minor_option_list_choice_and_complementary_module),
    ]
