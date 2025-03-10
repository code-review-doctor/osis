# Generated by Django 2.2.13 on 2021-09-30 14:12

from django.db import migrations


def get_score_sheet_address_with_cohort_name_field_queryset(apps):
    ScoreSheetAddress = apps.get_model("assessments", "ScoreSheetAddress")

    return ScoreSheetAddress.objects.filter(
        cohort_name__isnull=False
    )


def correct_education_group_fields(apps, schema_editor):
    print("Correct education_group field of score sheet addresses")
    addresses_to_correct_education_group = get_score_sheet_address_with_cohort_name_field_queryset(apps)
    for address in addresses_to_correct_education_group:
        try:
            correct_education_group_field(address, apps)
        except Exception as e:
            print("- {} (error) {}".format(address.id, e))


def correct_education_group_field(address, apps):
    EducationGroupYear = apps.get_model("base", "EducationGroupYear")
    acronym_11ba = address.education_group.educationgroupyear_set.filter(
        education_group_id=address.education_group.id
    ).latest(
        'academic_year__year'
    ).acronym
    if acronym_11ba.endswith('11BA'):
        acronym_1ba = acronym_11ba.replace('11BA', '1BA')
        eg_1ba = EducationGroupYear.objects.filter(
            acronym=acronym_1ba
        ).select_related(
            'education_group'
        ).last().education_group
        address.education_group = eg_1ba
        address.save()
        print("- {}".format(address.id))


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0009_email_soumission'),
    ]

    operations = [
        migrations.RunPython(
            correct_education_group_fields
        ),
    ]
