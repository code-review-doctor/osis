# Generated by Django 2.2.13 on 2021-01-04 10:24
import datetime

from django.db import migrations
from django.utils import timezone

from base.models.enums.academic_calendar_type import AcademicCalendarTypes


def remove_education_group_academic_calendar(apps, shema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    AcademicCalendar.objects.filter(
        reference__in=[
            AcademicCalendarTypes.EDUCATION_GROUP_EDITION.name,
            AcademicCalendarTypes.EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT.name,
            AcademicCalendarTypes.EDUCATION_GROUP_LIMITED_DAILY_MANAGEMENT.name,
        ]
    ).delete()


def create_education_group_academic_calendar(apps, shema_editor):
    """
    We will create all calendars which are mandatory to education group app
    """
    # Create older calendars from EDUCATION_GROUP_EDITION to N + 6
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    if current_academic_year:
        qs = AcademicYear.objects.filter(year__gte=2019, year__lte=current_academic_year.year + 6)
        for ac_year in qs:
            _create_education_group_preparation_calendar(AcademicCalendar, ac_year)
            _create_education_group_extended_daily_management_calendar(AcademicCalendar, ac_year)
            _create_education_group_limited_daily_management_calendar(AcademicCalendar, ac_year)


def _create_education_group_preparation_calendar(academic_calendar_cls, targeted_academic_year):
    academic_calendar_cls.objects.update_or_create(
        reference=AcademicCalendarTypes.EDUCATION_GROUP_EDITION.name,
        data_year=targeted_academic_year,
        defaults={
            "title": "Préparation des formations",
            "start_date": datetime.date(targeted_academic_year.year - 1, 8, 15),
            "end_date": datetime.date(targeted_academic_year.year - 1, 11, 20),
            "academic_year": targeted_academic_year
        }
    )


def _create_education_group_extended_daily_management_calendar(academic_calendar_cls, targeted_academic_year):
    academic_calendar_cls.objects.update_or_create(
        reference=AcademicCalendarTypes.EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT.name,
        data_year=targeted_academic_year,
        defaults={
            "title": "Gestion journalière étendue - catalogue",
            "start_date": datetime.date(targeted_academic_year.year - 6, 9, 15),
            "end_date": None,
            "academic_year": targeted_academic_year
        }
    )


def _create_education_group_limited_daily_management_calendar(academic_calendar_cls, targeted_academic_year):
    academic_calendar_cls.objects.update_or_create(
        reference=AcademicCalendarTypes.EDUCATION_GROUP_LIMITED_DAILY_MANAGEMENT.name,
        data_year=targeted_academic_year,
        defaults={
            "title": "Gestion journalière limitée - catalogue",
            "start_date": datetime.date(targeted_academic_year.year - 2, 9, 15),
            "end_date": None,
            "academic_year": targeted_academic_year
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ('education_group', '0012_copy_title_english_from_egy_to_gy'),
    ]

    operations = [
        migrations.RunPython(create_education_group_academic_calendar, remove_education_group_academic_calendar, elidable=True),
    ]
