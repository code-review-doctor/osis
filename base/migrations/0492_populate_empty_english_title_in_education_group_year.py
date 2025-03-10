# Generated by Django 2.2.5 on 2020-01-06 14:49

from django.db import migrations

from base.models.enums.education_group_categories import TRAINING, MINI_TRAINING


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0491_auto_20200107_1458'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE base_educationgroupyear "
            "SET title_english=title "
            "FROM base_academicyear AS ay, base_educationgrouptype AS egt "
            "WHERE base_educationgroupyear.academic_year_id=ay.id "
            "AND (title_english is null or title_english = '' ) AND ay.year >= 2019 "
            "AND egt.category in ('" + TRAINING + "', '" + MINI_TRAINING+"') "
            "AND base_educationgroupyear.education_group_type_id=egt.id;",
            elidable=True
        )
    ]
