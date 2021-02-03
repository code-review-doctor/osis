# Generated by Django 2.2.13 on 2021-01-27 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0560_auto_20210120_0845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academiccalendar',
            name='reference',
            field=models.CharField(choices=[('DELIBERATION', 'Deliberation'), ('DISSERTATION_SUBMISSION', 'Dissertation submission'), ('EXAM_ENROLLMENTS', 'Exam enrollments'), ('SCORES_EXAM_DIFFUSION', 'Scores exam diffusion'), ('SCORES_EXAM_SUBMISSION', 'Scores exam submission'), ('TEACHING_CHARGE_APPLICATION', 'Application for vacant courses'), ('COURSE_ENROLLMENT', 'Course enrollment'), ('SUMMARY_COURSE_SUBMISSION', 'Summary course submission'), ('SUMMARY_COURSE_SUBMISSION_FORCE_MAJEURE', 'Summary course submission force majeure'), ('EDUCATION_GROUP_SWITCH', 'Education group switch'), ('EDUCATION_GROUP_EDITION', 'Education group edition'), ('EDUCATION_GROUP_EXTENDED_DAILY_MANAGEMENT', 'Education group extended daily management'), ('EDUCATION_GROUP_LIMITED_DAILY_MANAGEMENT', 'Education group limited daily management'), ('LEARNING_UNIT_EDITION_CENTRAL_MANAGERS', 'Learning unit edition by central managers'), ('LEARNING_UNIT_EDITION_FACULTY_MANAGERS', 'Learning unit edition by faculty managers'), ('LEARNING_UNIT_EXTENDED_PROPOSAL_MANAGEMENT', 'Extended proposal management'), ('LEARNING_UNIT_LIMITED_PROPOSAL_MANAGEMENT', 'Limited proposal management'), ('CREATION_OR_END_DATE_PROPOSAL_CENTRAL_MANAGERS', 'Creation or end date proposal by central managers'), ('CREATION_OR_END_DATE_PROPOSAL_FACULTY_MANAGERS', 'Creation or end date proposal by faculty managers'), ('MODIFICATION_OR_TRANSFORMATION_PROPOSAL_CENTRAL_MANAGERS', 'Modification or transformation proposal by central managers'), ('MODIFICATION_OR_TRANSFORMATION_PROPOSAL_FACULTY_MANAGERS', 'Modification or transformation proposal by faculty managers')], max_length=70),
        ),
    ]
