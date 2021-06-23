# Generated by Django 2.2.13 on 2021-06-01 06:20
import re

from django.db import migrations
from django.db.models import Q

BAC_CODE = '1BA'
STARTING_YEAR_TO_FILL_GAP = 2022


def remove_11ba_in_cohort_year(apps, shema_editor):
    CohortYear = apps.get_model('education_group', 'cohortyear')
    EducationGroupYear = apps.get_model('base', 'educationgroupyear')

    all_11bas = EducationGroupYear.objects.filter(acronym__endswith='11BA')
    pattern_11ba = re.compile(r'11BA')
    corresponding_trainings = []
    for my_11ba in all_11bas:
        acronym_1ba = pattern_11ba.sub(BAC_CODE, my_11ba.acronym)
        corresponding_trainings.append(
            EducationGroupYear.objects.get(
                acronym=acronym_1ba,
                academic_year=my_11ba.academic_year
            )
        )
    CohortYear.objects.filter(
        education_group_year__in=corresponding_trainings,
        name='FIRST_YEAR'
    ).delete()


def copy_existing_11ba_in_cohort_year(apps, shema_editor):
    CohortYear = apps.get_model('education_group', 'cohortyear')
    EducationGroupYear = apps.get_model('base', 'educationgroupyear')

    all_11bas = EducationGroupYear.objects.filter(acronym__endswith='11BA')
    pattern_11ba = re.compile(r'11BA')
    for my_11ba in all_11bas:
        acronym_1ba = pattern_11ba.sub(BAC_CODE, my_11ba.acronym)
        corresponding_training = EducationGroupYear.objects.get(
            acronym=acronym_1ba,
            academic_year=my_11ba.academic_year
        )
        if corresponding_training.administration_entity == my_11ba.administration_entity:
            administration_entity = None
        else:
            administration_entity = my_11ba.administration_entity
        CohortYear.objects.update_or_create(
            education_group_year=corresponding_training,
            name='FIRST_YEAR',
            defaults={
                "administration_entity": administration_entity,
            }
        )


def create_default_11ba_in_cohort_year(apps, shema_editor):
    CohortYear = apps.get_model('education_group', 'cohortyear')
    EducationGroupYear = apps.get_model('base', 'educationgroupyear')

    bac_with_11ba = CohortYear.objects.filter(
        education_group_year__academic_year__year__gte=STARTING_YEAR_TO_FILL_GAP
    ).values_list('education_group_year__id', flat=True)

    all_1bas_without_cohort = EducationGroupYear.objects.filter(
        education_group_type__name='BACHELOR',
        academic_year__year__gte=STARTING_YEAR_TO_FILL_GAP
    ).exclude(
        pk__in=bac_with_11ba
    ).exclude(
        Q(acronym__endswith='11BA') | Q(acronym='common-1ba')
    )

    for my_1ba in all_1bas_without_cohort:
        try:
            last_existing_cohort = CohortYear.objects.filter(
                education_group_year__acronym=my_1ba.acronym,
                name='FIRST_YEAR'
            ).select_related(
                'education_group_year'
            ).prefetch_related(
                'education_group_year__academic_year'
            ).latest('education_group_year__academic_year__year')
        except CohortYear.DoesNotExist:
            last_existing_cohort = None
        CohortYear.objects.update_or_create(
            education_group_year=my_1ba,
            name='FIRST_YEAR',
            defaults={
                "administration_entity": last_existing_cohort.administration_entity if last_existing_cohort else None,
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('education_group', '0022_auto_20210531_1115'),
    ]

    operations = [
        migrations.RunPython(copy_existing_11ba_in_cohort_year, remove_11ba_in_cohort_year),
        migrations.RunPython(create_default_11ba_in_cohort_year, migrations.RunPython.noop),
    ]
