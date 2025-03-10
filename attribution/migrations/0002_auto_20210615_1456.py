# Generated by Django 2.2.13 on 2021-06-15 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0001_squashed_0045_auto_20210318_0949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribution',
            name='function',
            field=models.CharField(blank=True, choices=[('COORDINATOR', 'Coordinator'), ('HOLDER', 'Holder'), ('CO_HOLDER', 'Co-holder'), ('DEPUTY', 'Deputy'), ('DEPUTY_AUTHORITY', 'Deputy authority'), ('DEPUTY_SABBATICAL', 'Deputy sabbatical'), ('DEPUTY_TEMPORARY', 'Deputy temporary'), ('PROFESSOR', 'Professor'), ('INTERNSHIP_SUPERVISOR', 'Internship supervisor'), ('INTERNSHIP_CO_SUPERVISOR', 'Internship co-supervisor'), ('DEPUTY_DISEASE_OR_MATERNITY', 'Deputy disease or maternity')], db_index=True, max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='attributionnew',
            name='function',
            field=models.CharField(choices=[('COORDINATOR', 'Coordinator'), ('HOLDER', 'Holder'), ('CO_HOLDER', 'Co-holder'), ('DEPUTY', 'Deputy'), ('DEPUTY_AUTHORITY', 'Deputy authority'), ('DEPUTY_SABBATICAL', 'Deputy sabbatical'), ('DEPUTY_TEMPORARY', 'Deputy temporary'), ('PROFESSOR', 'Professor'), ('INTERNSHIP_SUPERVISOR', 'Internship supervisor'), ('INTERNSHIP_CO_SUPERVISOR', 'Internship co-supervisor'), ('DEPUTY_DISEASE_OR_MATERNITY', 'Deputy disease or maternity')], db_index=True, max_length=35, verbose_name='Function'),
        ),
        migrations.AlterField(
            model_name='tutorapplication',
            name='function',
            field=models.CharField(blank=True, choices=[('COORDINATOR', 'Coordinator'), ('HOLDER', 'Holder'), ('CO_HOLDER', 'Co-holder'), ('DEPUTY', 'Deputy'), ('DEPUTY_AUTHORITY', 'Deputy authority'), ('DEPUTY_SABBATICAL', 'Deputy sabbatical'), ('DEPUTY_TEMPORARY', 'Deputy temporary'), ('PROFESSOR', 'Professor'), ('INTERNSHIP_SUPERVISOR', 'Internship supervisor'), ('INTERNSHIP_CO_SUPERVISOR', 'Internship co-supervisor'), ('DEPUTY_DISEASE_OR_MATERNITY', 'Deputy disease or maternity')], db_index=True, max_length=35, null=True),
        ),
    ]
