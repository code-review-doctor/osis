from django.db import migrations

CALENDAR_REFERENCE = 'SCORES_EXAM_SUBMISSION'


def update_first_session_dates(apps, schema_editor):
    AcademicCalendar = apps.get_model('base', 'AcademicCalendar')
    qs = AcademicCalendar.objects.filter(
        reference=CALENDAR_REFERENCE,
        data_year__year__gte=2022,
        sessionexamcalendar__number_session=1
    )
    for calendar in qs:
        calendar.start_date = calendar.start_date.replace(day=6)
        calendar.save()


def update_third_session_dates(apps, schema_editor):
    AcademicCalendar = apps.get_model('base', 'AcademicCalendar')
    qs = AcademicCalendar.objects.filter(
        reference=CALENDAR_REFERENCE,
        data_year__year__gte=2021,
        sessionexamcalendar__number_session=3
    )

    for calendar in qs:
        calendar.start_date = calendar.start_date.replace(day=1)
        calendar.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0623_auto_20220216_1444'),
    ]

    operations = [
        migrations.RunPython(update_first_session_dates, reverse_code=lambda *args, **kwargs: None, elidable=True),
        migrations.RunPython(update_third_session_dates, reverse_code=lambda *args, **kwargs: None, elidable=True)
    ]
