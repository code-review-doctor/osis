# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-02 14:39
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0004_educationinstitution'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssimilationCriteria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('criteria', models.CharField(max_length=255, unique=True)),
                ('order', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EducationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('type', models.CharField(choices=[('TRANSITION', 'Transition'), ('QUALIFICATION', 'Qualification'), ('ANOTHER', 'Autre')], max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('adhoc', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExternalOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(null=True)),
                ('name', models.CharField(max_length=150, unique=True)),
                ('adhoc', models.BooleanField(default=True)),
                ('national', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='GradeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(max_length=255)),
                ('coverage', models.CharField(choices=[('HIGH_EDUC_NOT_UNIVERSITY', 'HIGH_EDUC_NOT_UNIVERSITY'), ('UNIVERSITY', 'UNIVERSITY'), ('UNKNOWN', 'UNKNOWN')], default='UNKNOWN', max_length=30)),
                ('adhoc', models.BooleanField(default=True)),
                ('institutional', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='InstitutionalGradeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='domain',
            name='adhoc',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='domain',
            name='national',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='domain',
            name='reference',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='domain',
            name='type',
            field=models.CharField(choices=[('HIGH_EDUC_NOT_UNIVERSITY', 'HIGH_EDUC_NOT_UNIVERSITY'), ('UNIVERSITY', 'UNIVERSITY'), ('UNKNOWN', 'UNKNOWN')], default='UNKNOWN', max_length=50),
        ),
        migrations.AddField(
            model_name='language',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='domain',
            name='decree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.Decree'),
        ),
        migrations.AlterField(
            model_name='educationinstitution',
            name='adhoc',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='educationinstitution',
            name='institution_type',
            field=models.CharField(choices=[('SECONDARY', 'SECONDARY'), ('UNIVERSITY', 'UNIVERSITY'), ('HIGHER_NON_UNIVERSITY', 'HIGHER_NON_UNIVERSITY')], max_length=25),
        ),
        migrations.AlterField(
            model_name='educationinstitution',
            name='national_community',
            field=models.CharField(blank=True, choices=[('FRENCH', 'FRENCH'), ('GERMAN', 'GERMAN'), ('DUTCH', 'DUTCH')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='gradetype',
            name='institutional_grade_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.InstitutionalGradeType'),
        ),
        migrations.AddField(
            model_name='externaloffer',
            name='domain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Domain'),
        ),
        migrations.AddField(
            model_name='externaloffer',
            name='grade_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.GradeType'),
        ),
        migrations.AddField(
            model_name='externaloffer',
            name='offer_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.OfferYear'),
        ),
    ]
