# Generated by Django 2.2.13 on 2021-01-15 12:14

import datetime

from django.db import migrations
from django.db.models import F
from django.utils import timezone

from base.models.enums.academic_calendar_type import AcademicCalendarTypes

START_YEAR = 2020


def create_proposal_limited_calendar(apps, schema_editor):
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    if current_academic_year:
        qs = AcademicYear.objects.filter(year__gte=START_YEAR, year__lte=current_academic_year.year + 6)
        for ac_year in qs:
            AcademicCalendar.objects.update_or_create(
                reference=AcademicCalendarTypes.LEARNING_UNIT_LIMITED_PROPOSAL_MANAGEMENT.name,
                data_year=ac_year,
                defaults={
                    "title": "Gestion des propositions limitée",
                    "start_date": datetime.date(ac_year.year - 2,  9, 14),
                    "end_date": datetime.date(ac_year.year, 9, 13),
                }
            )


def create_proposal_extended_calendar(apps, schema_editor):
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    if current_academic_year:
        qs = AcademicYear.objects.filter(year__gte=START_YEAR, year__lte=current_academic_year.year + 6)
        for ac_year in qs:
            AcademicCalendar.objects.update_or_create(
                reference=AcademicCalendarTypes.LEARNING_UNIT_EXTENDED_PROPOSAL_MANAGEMENT.name,
                data_year=ac_year,
                defaults={
                    "title": "Gestion des propositions étendue",
                    "start_date": datetime.date(ac_year.year - 6,  9, 14),
                    "end_date": datetime.date(ac_year.year + 1, 9, 13),
                }
            )


def remove_proposal_limited_calendar(apps, schema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    AcademicCalendar.objects.filter(
        reference=AcademicCalendarTypes.LEARNING_UNIT_LIMITED_PROPOSAL_MANAGEMENT.name
    ).delete()


def remove_proposal_extended_calendar(apps, schema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    AcademicCalendar.objects.filter(
        reference=AcademicCalendarTypes.LEARNING_UNIT_EXTENDED_PROPOSAL_MANAGEMENT.name
    ).delete()


def remove_old_calendars(apps, schema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    references_to_delete = [
        "LEARNING_UNIT_EDITION_CENTRAL_MANAGERS",
        "LEARNING_UNIT_EDITION_FACULTY_MANAGERS",
        "CREATION_OR_END_DATE_PROPOSAL_CENTRAL_MANAGERS",
        "CREATION_OR_END_DATE_PROPOSAL_FACULTY_MANAGERS",
        "MODIFICATION_OR_TRANSFORMATION_PROPOSAL_CENTRAL_MANAGERS",
        "MODIFICATION_OR_TRANSFORMATION_PROPOSAL_FACULTY_MANAGERS"
    ]
    AcademicCalendar.objects.filter(reference__in=references_to_delete).delete()


def update_start_date_of_daily_management_calendars(apps, schema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    references_to_update = [
        AcademicCalendarTypes.EDUCATION_GROUP_LIMITED_DAILY_MANAGEMENT.name,
        AcademicCalendarTypes.EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT.name
    ]
    AcademicCalendar.objects.filter(
        reference__in=references_to_update,
        start_date__day=15
    ).update(
        start_date=F('start_date') - datetime.timedelta(days=1)
    )


class Migration(migrations.Migration):

    dependencies = [
        ('learning_unit', '0009_auto_20210203_1310'),
    ]

    operations = [
        migrations.RunPython(create_proposal_limited_calendar, remove_proposal_limited_calendar),
        migrations.RunPython(create_proposal_extended_calendar, remove_proposal_extended_calendar),
        migrations.RunPython(update_start_date_of_daily_management_calendars),
        migrations.RunPython(remove_old_calendars),
    ]
