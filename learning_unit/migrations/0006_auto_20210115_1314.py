# Generated by Django 2.2.13 on 2021-01-15 12:14

import datetime

from django.db import migrations
from django.utils import timezone

from base.models.enums import academic_calendar_type


def create_proposal_limited_calendar(apps, schema_editor):
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    if current_academic_year:
        qs = AcademicYear.objects.filter(year__gte=2015, year__lte=current_academic_year.year + 6)
        for ac_year in qs:
            AcademicCalendar.objects.update_or_create(
                reference=academic_calendar_type.LEARNING_UNIT_LIMITED_PROPOSAL_MANAGEMENT,
                data_year=ac_year,
                defaults={
                    "title": "Gestion des propositions limitée",
                    "start_date": datetime.date(ac_year.year - 2,  9, 15),
                    "end_date": datetime.date(ac_year.year, 9, 14),
                    "academic_year": ac_year
                }
            )


def create_proposal_extended_calendar(apps, schema_editor):
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    if current_academic_year:
        qs = AcademicYear.objects.filter(year__gte=2015, year__lte=current_academic_year.year + 6)
        for ac_year in qs:
            AcademicCalendar.objects.update_or_create(
                reference=academic_calendar_type.LEARNING_UNIT_EXTENDED_PROPOSAL_MANAGEMENT,
                data_year=ac_year,
                defaults={
                    "title": "Gestion des propositions étendue",
                    "start_date": datetime.date(ac_year.year - 6,  9, 15),
                    "end_date": datetime.date(ac_year.year + 1, 9, 14),
                    "academic_year": ac_year
                }
            )


def remove_proposal_limited_calendar(apps, schema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    AcademicCalendar.objects.filter(
        reference=academic_calendar_type.LEARNING_UNIT_LIMITED_PROPOSAL_MANAGEMENT
    ).delete()


def remove_proposal_extended_calendar(apps, schema_editor):
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    AcademicCalendar.objects.filter(
        reference=academic_calendar_type.LEARNING_UNIT_EXTENDED_PROPOSAL_MANAGEMENT
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('learning_unit', '0005_role_migration_centralmanager_facultymanager'),
    ]

    operations = [
        migrations.RunPython(create_proposal_limited_calendar(), remove_proposal_limited_calendar()),
        migrations.RunPython(create_proposal_extended_calendar(), remove_proposal_extended_calendar()),
    ]
