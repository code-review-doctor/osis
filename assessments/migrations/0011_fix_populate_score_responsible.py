# Generated by Django 2.2.13 on 2021-08-31 10:20

from django.db import migrations

ACADEMIC_YEAR = 2020


def get_queryset(apps):
    Attribution = apps.get_model("attribution", "Attribution")
    return Attribution.objects.filter(
        score_responsible=True,
        learning_unit_year__academic_year__year__gte=ACADEMIC_YEAR,
    ).select_related(
        "learning_unit_year",
        "tutor"
    )


def convert_attribution_to_score_responsible(apps, attribution_obj):
    ScoreResponsible = apps.get_model("assessments", "ScoreResponsible")
    obj, created = ScoreResponsible.objects.update_or_create(
        learning_unit_year=attribution_obj.learning_unit_year,
        tutor=attribution_obj.tutor,
        learning_class_year=None,
        defaults={}
    )
    return obj


def get_learning_unit_year_class(apps, luy):
    LearningClassYear = apps.get_model("learning_unit", "LearningClassYear")
    return LearningClassYear.objects.select_related(
        "learning_component_year",
        "learning_component_year__learning_unit_year"
    ).get(
        learning_component_year__learning_unit_year__acronym=luy.acronym[:-1],
        learning_component_year__learning_unit_year__academic_year=luy.academic_year,
        acronym=luy.acronym[-1]
    )


def create_score_responsible_for_class(apps, score_responsible_obj):
    ScoreResponsible = apps.get_model("assessments", "ScoreResponsible")
    LearningClassYear = apps.get_model("learning_unit", "LearningClassYear")
    try:
        class_year = get_learning_unit_year_class(apps, score_responsible_obj.learning_unit_year)
    except LearningClassYear.DoesNotExist:
        print('Could not create score responsible for class {}'.format(score_responsible_obj.learning_unit_year.acronym))
        return
    obj, created = ScoreResponsible.objects.update_or_create(
        pk=score_responsible_obj.pk,
        defaults={
            "external_id": score_responsible_obj.external_id,
            "learning_unit_year": class_year.learning_component_year.learning_unit_year,
            "learning_class_year": class_year,
        }
    )
    return obj


def is_learning_unit_year_a_class(luy):
    return luy.subtype == 'FULL' and luy.learning_container_year is None


def populate_score_responsible(apps, schema_editor):
    print("Removing all from ScoreResponsible table...")
    ScoreResponsible = apps.get_model("assessments", "ScoreResponsible")
    ScoreResponsible.objects.all().delete()
    print("Populate score responsible table")
    qs = get_queryset(apps)
    for attribution in qs:
        score_responsible_created = convert_attribution_to_score_responsible(apps, attribution)
        if is_learning_unit_year_a_class(score_responsible_created.learning_unit_year):
            create_score_responsible_for_class(apps, score_responsible_created)
        print("- {}".format(score_responsible_created.id))


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0010_mail_template_correction_encodage_complet'),
    ]

    operations = [
        migrations.RunPython(
            populate_score_responsible
        ),
    ]
