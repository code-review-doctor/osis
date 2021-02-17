# Generated by Django 2.2.13 on 2021-01-27 17:04
from django.db import migrations, models
import django.db.models.deletion


def set_session_exam_education_group_year_field(apps, schema_editor):
    SessionExam = apps.get_model('base', 'sessionexam')
    map_with_educ_group_id = _build_map(apps)
    to_update = []
    qs = SessionExam.objects.all().select_related(
        'offer_year__academic_year'
    ).order_by(
        'offer_year__academic_year__year',
        'offer_year__acronym',
    )
    errors = set()
    for obj in qs:
        if not obj.offer_year:
            print('WARNING :: offer_year field is null for id = {}. This record will be removed.'.format(obj.pk))
            continue
        acronym_with_year = obj.offer_year.acronym + str(obj.offer_year.academic_year.year)
        education_group_year = map_with_educ_group_id.get(acronym_with_year)
        if not education_group_year:
            msg = 'WARNING :: no EducationGroupYear found for {offer_year.acronym} {offer_year.academic_year.year}.'
            errors.add(msg.format(offer_year=obj.offer_year))
        else:
            obj.education_group_year_id = education_group_year.id
            to_update.append(obj)
    for msg in sorted(errors):
        print(msg)
    SessionExam.objects.bulk_update(to_update, ['education_group_year_id'], batch_size=1000)


def _build_map(apps):
    EducationGroupYear = apps.get_model('base', 'educationgroupyear')
    return {
        obj.acronym + str(obj.academic_year.year): obj
        for obj in EducationGroupYear.objects.all().select_related('academic_year')
    }


def populate_or_delete_educationgroup_year_id(apps, schema_editor):
    OfferEnrollment = apps.get_model('base', 'offerenrollment')
    EducationGroupYear = apps.get_model('base', 'educationgroupyear')
    off_enrollments_without_educ_group = OfferEnrollment.objects.filter(
        education_group_year_id__isnull=True
    ).select_related(
        'offer_year__academic_year'
    )
    deleted = set()
    for obj in off_enrollments_without_educ_group:
        education_group_year_id = EducationGroupYear.objects.filter(
            acronym=obj.offer_year.acronym,
            academic_year=obj.offer_year.academic_year,
        ).values_list('pk', flat=True).first()
        if not education_group_year_id:
            deleted.add('Removing all offerenrollments of {} in {}'.format(obj.offer_year.acronym, obj.offer_year.academic_year.year))
            obj.delete()
        else:
            obj.education_group_year_id = education_group_year_id
            obj.save()
    for msg in sorted(deleted):
        print(msg)


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0567_auto_20210211_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionexam',
            name='education_group_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupYear'),
        ),
        migrations.RunPython(set_session_exam_education_group_year_field),
        migrations.RunPython(populate_or_delete_educationgroup_year_id),
    ]
