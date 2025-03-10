# Generated by Django 2.2.13 on 2021-01-18 10:43
import datetime

from django.db import migrations
from django.utils import timezone

from base.models.enums.academic_calendar_type import AcademicCalendarTypes


def change_education_group_preparation_calendar(apps, shema_editor):
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    if current_academic_year:
        AcademicCalendar.objects.filter(
            academic_year__year__gte=2021, reference=AcademicCalendarTypes.EDUCATION_GROUP_EDITION.name
        ).delete()

        qs = AcademicYear.objects.filter(year__gte=2021, year__lte=current_academic_year.year + 6)
        for ac_year in qs:
            AcademicCalendar.objects.update_or_create(
                reference=AcademicCalendarTypes.EDUCATION_GROUP_EDITION.name,
                data_year=ac_year,
                defaults={
                    "title": "Préparation des formations",
                    "start_date": datetime.date(ac_year.year - 1, 7, 1),
                    "end_date": datetime.date(ac_year.year, 6, 1),
                    "academic_year": ac_year
                }
            )


class Migration(migrations.Migration):

    dependencies = [
        ('education_group', '0014_auto_20210112_0814'),
    ]

    operations = [
        migrations.RunPython(change_education_group_preparation_calendar, migrations.RunPython.noop, elidable=True),
    ]
