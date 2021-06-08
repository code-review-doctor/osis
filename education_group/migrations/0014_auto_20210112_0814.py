# Generated by Django 2.2.13 on 2021-01-12 08:14
import datetime

from django.db import migrations
from django.utils import timezone

from base.models.enums.academic_calendar_type import AcademicCalendarTypes


def create_education_group_switch_calendar(apps, shema_editor):
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    if current_academic_year:
        qs = AcademicYear.objects.filter(year__gte=2020, year__lte=current_academic_year.year + 6)
        for ac_year in qs:
            AcademicCalendar.objects.update_or_create(
                reference=AcademicCalendarTypes.EDUCATION_GROUP_SWITCH.name,
                data_year=ac_year,
                defaults={
                    "title": "Basculement des formations",
                    "start_date": datetime.date(ac_year.year, 7, 1),
                    "end_date": datetime.date(ac_year.year + 1, 6, 30),
                    "academic_year": ac_year
                }
            )


def remove_education_group_switch_calendar(apps, shema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    AcademicCalendar.objects.filter(reference=AcademicCalendarTypes.EDUCATION_GROUP_SWITCH.name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('education_group', '0013_auto_20210104_1024'),
    ]

    operations = [
        migrations.RunPython(create_education_group_switch_calendar, remove_education_group_switch_calendar, elidable=True),
    ]
