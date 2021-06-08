# Generated by Django 2.2.13 on 2021-05-25 12:56

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    replaces = [('attribution', '0001_initial'),
                ('attribution', '0002_move_data_from_base_attribution_to_attribution_attribution'),
                ('attribution', '0003_auto_20161215_1420'), ('attribution', '0004_attribution_score_responsible'),
                ('attribution', '0005_from_coordinator_to_score_responsible'),
                ('attribution', '0006_auto_20161216_1338'), ('attribution', '0007_attribution_uuid'),
                ('attribution', '0008_populate_uuid_values'), ('attribution', '0009_uuid_not_null'),
                ('attribution', '0010_move_data_from_base_attribution_to_attribution_attribution'),
                ('attribution', '0011_auto_20170123_1025'), ('attribution', '0012_auto_20170203_0950'),
                ('attribution', '0013_auto_20170607_1522'), ('attribution', '0014_auto_20170627_1426'),
                ('attribution', '0015_attribution_deleted'), ('attribution', '0016_auto_20171018_0937'),
                ('attribution', '0017_auto_20171027_1706'), ('attribution', '0018_auto_20171208_0056'),
                ('attribution', '0019_auto_20180103_1427'), ('attribution', '0020_auto_20180105_1021'),
                ('attribution', '0021_attributionnew_substitute'), ('attribution', '0022_auto_20180115_0913'),
                ('attribution', '0023_auto_20180116_1026'), ('attribution', '0024_auto_20180116_1034'),
                ('attribution', '0025_auto_20180116_1052'), ('attribution', '0026_auto_20180116_1052'),
                ('attribution', '0027_auto_20180117_1322'), ('attribution', '0028_auto_20180129_1308'),
                ('attribution', '0029_WARNING_INDEX_20180129_1441'), ('attribution', '0030_auto_20180228_0856'),
                ('attribution', '0031_remove_attributionnew_summary_responsible'),
                ('attribution', '0032_auto_20180327_1458'), ('attribution', '0033_auto_20180327_1513'),
                ('attribution', '0034_auto_20180807_1229'), ('attribution', '0035_attributionchargenew_changed'),
                ('attribution', '0036_auto_20181105_1501'), ('attribution', '0037_auto_20181116_1050'),
                ('attribution', '0038_auto_20191206_1519'), ('attribution', '0039_auto_20200319_1305'),
                ('attribution', '0040_attributionnew_decision_making'), ('attribution', '0041_auto_20210121_1336'),
                ('attribution', '0041_auto_20210115_1109'), ('attribution', '0042_merge_20210126_0900'),
                ('attribution', '0043_auto_20210224_1137'), ('attribution', '0044_remove_attribution_uuid'),
                ('attribution', '0045_auto_20210318_0949')]

    initial = True

    dependencies = [
        ('base', '0001_squashed_0497_auto_20200108_1213'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributionNew',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('function', models.CharField(choices=[('COORDINATOR', 'Coordinator'), ('HOLDER', 'Holder'), ('CO_HOLDER', 'Co-holder'), ('DEPUTY', 'Deputy'), ('DEPUTY_AUTHORITY', 'Deputy authority'), ('DEPUTY_SABBATICAL', 'Deputy sabbatical'), ('DEPUTY_TEMPORARY', 'Deputy temporary'), ('PROFESSOR', 'Professor'), ('INTERNSHIP_SUPERVISOR', 'Internship supervisor'), ('INTERNSHIP_CO_SUPERVISOR', 'Internship co-supervisor')], db_index=True, max_length=35, verbose_name='Function')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('start_year', models.IntegerField(blank=True, null=True, verbose_name='Start')),
                ('end_year', models.IntegerField(blank=True, null=True)),
                ('score_responsible', models.BooleanField(default=False)),
                ('learning_container_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.LearningContainerYear')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Tutor')),
                ('substitute', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Person')),
                ('decision_making', models.CharField(blank=True, choices=[('PROGRAM_MODIFICATION', 'Program modification'), ('DISCHARGE', 'Discharge'), ('TEACHING_SUPPLY', 'Teaching supply'), ('AUTHORITY_OR_SABBATICAL_TEACHING_SUPPLY', 'Authority/sabbatical teaching supply'), ('DEMAND_FOR_DISCHARGE', 'Demand for discharge'), ('DEMAND_FOR_CO_HOLDER', 'Demand for co-holder'), ('CO_HOLDER', 'Co-holder'), ('TO_DELETE', 'To delete'), ('PART_TIME_TEACHING_SUPPLY', 'Part-time teaching supply')], default='', max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='AttributionChargeNew',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('allocation_charge', models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('attribution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attribution.AttributionNew')),
                ('learning_component_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.LearningComponentYear')),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Attribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('function', models.CharField(blank=True, choices=[('COORDINATOR', 'Coordinator'), ('HOLDER', 'Holder'), ('CO_HOLDER', 'Co-holder'), ('DEPUTY', 'Deputy'), ('DEPUTY_AUTHORITY', 'Deputy authority'), ('DEPUTY_SABBATICAL', 'Deputy sabbatical'), ('DEPUTY_TEMPORARY', 'Deputy temporary'), ('PROFESSOR', 'Professor'), ('INTERNSHIP_SUPERVISOR', 'Internship supervisor'), ('INTERNSHIP_CO_SUPERVISOR', 'Internship co-supervisor')], db_index=True, max_length=35, null=True)),
                ('learning_unit_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.LearningUnitYear')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Tutor')),
                ('score_responsible', models.BooleanField(default=False)),
                ('end_year', models.IntegerField(blank=True, null=True)),
                ('start_year', models.IntegerField(blank=True, null=True)),
                ('summary_responsible', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TutorApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('function', models.CharField(blank=True, choices=[('COORDINATOR', 'Coordinator'), ('HOLDER', 'Holder'), ('CO_HOLDER', 'Co-holder'), ('DEPUTY', 'Deputy'), ('DEPUTY_AUTHORITY', 'Deputy authority'), ('DEPUTY_SABBATICAL', 'Deputy sabbatical'), ('DEPUTY_TEMPORARY', 'Deputy temporary'), ('PROFESSOR', 'Professor'), ('INTERNSHIP_SUPERVISOR', 'Internship supervisor'), ('INTERNSHIP_CO_SUPERVISOR', 'Internship co-supervisor')], db_index=True, max_length=35, null=True)),
                ('volume_lecturing', models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True)),
                ('volume_pratical_exercice', models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True)),
                ('learning_container_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.LearningContainerYear')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Tutor')),
                ('course_summary', models.TextField(blank=True, null=True)),
                ('last_changed', models.DateTimeField(null=True)),
                ('remark', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
