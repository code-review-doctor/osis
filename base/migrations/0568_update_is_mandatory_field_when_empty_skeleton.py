# Generated by Django 2.2.13 on 2021-02-22 13:33
import datetime

from django.db import migrations

from base.models.enums import education_group_types, education_group_categories

YEAR = 2020


def get_base_skeleton_per_type():
    return {
        education_group_types.TrainingType.AGGREGATION.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.CERTIFICATE_OF_PARTICIPATION.name: [
            education_group_types.GroupType.COMMON_CORE.name
        ],
        education_group_types.TrainingType.CERTIFICATE_OF_SUCCESS.name: [
            education_group_types.GroupType.COMMON_CORE.name
        ],
        education_group_types.TrainingType.CERTIFICATE_OF_HOLDING_CREDITS.name: [
            education_group_types.GroupType.COMMON_CORE.name
        ],
        education_group_types.TrainingType.BACHELOR.name: [education_group_types.GroupType.COMMON_CORE.name,
                                                           education_group_types.GroupType.MINOR_LIST_CHOICE.name,
                                                           education_group_types.GroupType.MAJOR_LIST_CHOICE.name],
        education_group_types.TrainingType.CERTIFICATE.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.CAPAES.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.RESEARCH_CERTIFICATE.name: [
            education_group_types.GroupType.COMMON_CORE.name
        ],
        education_group_types.TrainingType.UNIVERSITY_FIRST_CYCLE_CERTIFICATE.name: [
            education_group_types.GroupType.COMMON_CORE.name
        ],
        education_group_types.TrainingType.UNIVERSITY_SECOND_CYCLE_CERTIFICATE.name: [
            education_group_types.GroupType.COMMON_CORE.name
        ],
        education_group_types.TrainingType.ACCESS_CONTEST.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.LANGUAGE_CLASS.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.ISOLATED_CLASS.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.PHD.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.FORMATION_PHD.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.JUNIOR_YEAR.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.PGRM_MASTER_120.name: [
            education_group_types.GroupType.COMMON_CORE.name,
            education_group_types.GroupType.FINALITY_120_LIST_CHOICE.name,
            education_group_types.GroupType.OPTION_LIST_CHOICE.name,
            education_group_types.GroupType.COMPLEMENTARY_MODULE.name
        ],
        education_group_types.TrainingType.MASTER_MA_120.name: [
            education_group_types.GroupType.COMMON_CORE.name,
            education_group_types.GroupType.OPTION_LIST_CHOICE.name
        ],
        education_group_types.TrainingType.MASTER_MD_120.name: [
            education_group_types.GroupType.COMMON_CORE.name,
            education_group_types.GroupType.OPTION_LIST_CHOICE.name
        ],
        education_group_types.TrainingType.MASTER_MS_120.name: [
            education_group_types.GroupType.COMMON_CORE.name,
            education_group_types.GroupType.OPTION_LIST_CHOICE.name
        ],
        education_group_types.TrainingType.PGRM_MASTER_180_240.name: [
            education_group_types.GroupType.COMMON_CORE.name,
            education_group_types.GroupType.FINALITY_180_LIST_CHOICE.name
        ],
        education_group_types.TrainingType.MASTER_MA_180_240.name: [
            education_group_types.GroupType.COMMON_CORE.name,
            education_group_types.GroupType.OPTION_LIST_CHOICE.name
        ],
        education_group_types.TrainingType.MASTER_MD_180_240.name: [
            education_group_types.GroupType.COMMON_CORE.name,
            education_group_types.GroupType.OPTION_LIST_CHOICE.name
        ],
        education_group_types.TrainingType.MASTER_MS_180_240.name: [
            education_group_types.GroupType.COMMON_CORE.name,
            education_group_types.GroupType.OPTION_LIST_CHOICE.name
        ],
        education_group_types.TrainingType.MASTER_M1.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.MASTER_MC.name: [education_group_types.GroupType.COMMON_CORE.name],
        education_group_types.TrainingType.INTERNSHIP.name: [education_group_types.GroupType.COMMON_CORE.name],
    }


def is_skeleton_empty(apps, group_year) -> bool:
    GroupElementYear = apps.get_model('base', 'GroupElementYear')
    common_cores = GroupElementYear.objects.filter(
        parent_element__group_year=group_year,
        child_element__group_year__education_group_type__name=education_group_types.GroupType.COMMON_CORE.name
    )
    common_core = [c.child_element.id for c in common_cores]

    child_of_common_core = GroupElementYear.objects \
        .filter(parent_element__id__in=common_core) \
        .exclude(child_element__isnull=True)
    return len(child_of_common_core) == 0


def update_skeleton(apps, group_year) -> int:
    GroupElementYear = apps.get_model('base', 'GroupElementYear')
    parent_group_type = group_year.education_group_type.name
    skeleton = GroupElementYear.objects.filter(
        parent_element__group_year=group_year,
        child_element__group_year__education_group_type__name__in=get_base_skeleton_per_type()[parent_group_type],
        is_mandatory=False
    )
    return skeleton.update(is_mandatory=True)


def update_to_mandatory(apps) -> int:
    GroupYear = apps.get_model('education_group', 'GroupYear')
    parent_elements_group_year = GroupYear.objects.filter(
        academic_year__year__gte=YEAR,
        education_group_type__category=education_group_categories.TRAINING
    )
    record_modified = 0
    for group_year in parent_elements_group_year:
        if is_skeleton_empty(apps, group_year):
            record_modified += update_skeleton(apps, group_year)

    return record_modified


def run(apps, schema_editor):
    GroupElementYear = apps.get_model('base', 'GroupElementYear')
    GroupYear = apps.get_model('education_group', 'GroupYear')
    start_time = datetime.datetime.now()
    print("\n\tUpdate to mandatory for empty skeleton with year_gte: {}".format(YEAR))
    result = update_to_mandatory(apps)
    print('\t{} GroupElementYear updated'.format(result))
    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    print('\tTotal time:', total_time)


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0567_auto_20210211_0843'),
    ]

    operations = [
        migrations.RunPython(run),
    ]
