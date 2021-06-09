# Generated by Django 2.2.13 on 2021-01-29 09:01
import datetime

from django.db import migrations
from django.utils import timezone

from base.models.enums.academic_calendar_type import AcademicCalendarTypes


def change_exam_enrollment_calendar(apps, shema_editor):
    AcademicYear = apps.get_model('base', 'academicyear')
    AcademicCalendar = apps.get_model('base', 'academiccalendar')
    SessionExamCalendar = apps.get_model('base', 'sessionexamcalendar')

    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).last()
    if current_academic_year:
        SessionExamCalendar.objects.filter(
            academic_calendar__data_year__year__gte=2021,
            academic_calendar__reference=AcademicCalendarTypes.EXAM_ENROLLMENTS.name,
        ).delete()
        AcademicCalendar.objects.filter(
            academic_year__year__gte=2021, reference=AcademicCalendarTypes.EXAM_ENROLLMENTS.name
        ).delete()

        qs = AcademicYear.objects.filter(year__gte=2021, year__lte=current_academic_year.year + 6)
        for ac_year in qs:
            # Create session 1
            academic_calendar_1 = AcademicCalendar.objects.create(
                reference=AcademicCalendarTypes.EXAM_ENROLLMENTS.name,
                data_year=ac_year,
                title="Inscriptions aux examens - Session d'examens n°1",
                start_date=datetime.date(ac_year.year, 11, 1),
                end_date=datetime.date(ac_year.year, 11, 30),
                academic_year=ac_year
            )
            SessionExamCalendar.objects.create(number_session=1, academic_calendar=academic_calendar_1)

            # Create session 2
            academic_calendar_2 = AcademicCalendar.objects.create(
                reference=AcademicCalendarTypes.EXAM_ENROLLMENTS.name,
                data_year=ac_year,
                title="Inscriptions aux examens - Session d'examens n°2",
                start_date=datetime.date(ac_year.year + 1, 3, 1),
                end_date=datetime.date(ac_year.year + 1, 4, 30),
                academic_year=ac_year

            )
            SessionExamCalendar.objects.create(number_session=2, academic_calendar=academic_calendar_2)

            # Create session 3
            academic_calendar_3 = AcademicCalendar.objects.create(
                reference=AcademicCalendarTypes.EXAM_ENROLLMENTS.name,
                data_year=ac_year,
                title="Inscriptions aux examens - Session d'examens n°3",
                start_date=datetime.date(ac_year.year + 1, 6, 15),
                end_date=datetime.date(ac_year.year + 1, 7, 15),
                academic_year=ac_year  # To remove after refactoring
            )
            SessionExamCalendar.objects.create(number_session=3, academic_calendar=academic_calendar_3)


class Migration(migrations.Migration):

    dependencies = [
        ('education_group', '0015_auto_20210118_1043'),
    ]

    operations = [
        migrations.RunPython(change_exam_enrollment_calendar, migrations.RunPython.noop, elidable=True),
    ]
