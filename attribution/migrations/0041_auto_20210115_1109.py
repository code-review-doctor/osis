# Generated by Django 2.2.13 on 2021-01-15 11:09
import datetime

from django.db import migrations
from django.utils import timezone

from base.models.enums import academic_calendar_type


def create_application_courses_calendar(apps, shema_editor):
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    if current_academic_year:
        qs = AcademicYear.objects.filter(year__gte=2015, year__lte=current_academic_year.year + 6)
        for ac_year in qs:
            AcademicCalendar.objects.update_or_create(
                reference=academic_calendar_type.TEACHING_CHARGE_APPLICATION,
                data_year=ac_year,
                defaults={
                    "title": "Candidature aux cours vacants",
                    "start_date": datetime.date(ac_year.year, 2, 15),
                    "end_date": datetime.date(ac_year.year, 2, 28),
                    "academic_year": ac_year
                }
            )


def remove_application_courses_calendar(apps, shema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    AcademicCalendar.objects.filter(reference=academic_calendar_type.TEACHING_CHARGE_APPLICATION).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0040_attributionnew_decision_making'),
    ]

    operations = [
        migrations.RunPython(create_application_courses_calendar, remove_application_courses_calendar),
    ]
