from django.db import migrations


def fill_person_column_in_tutor_application_table(apps, schema_editor):
    TutorApplication = apps.get_model('attribution', 'TutorApplication')

    qs = TutorApplication.objects.select_related('tutor').all()
    for row in qs:
        row.person_id = row.tutor.person_id
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0011_auto_20220106_0852'),
    ]

    operations = [
        migrations.RunPython(fill_person_column_in_tutor_application_table, migrations.RunPython.noop, elidable=True),
    ]
