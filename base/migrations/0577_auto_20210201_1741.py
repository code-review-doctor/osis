# Generated by Django 2.2.14 on 2021-02-01 17:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0576_populate_not_null_fields'),
        # ('continuing_education', '0084_auto_20210127_1119'),
        ('dissertation', '0051_auto_20191211_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offerenrollment',
            name='education_group_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.EducationGroupYear'),
        ),
        migrations.AlterField(
            model_name='offeryearcalendar',
            name='education_group_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupYear'),
        ),
        migrations.AlterField(
            model_name='sessionexam',
            name='education_group_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupYear'),
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='academic_year',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='campus',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='country',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='entity_administration',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='entity_administration_fac',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='entity_management',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='entity_management_fac',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='grade_type',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='offer',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='offer_type',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='offeryeardomain',
            name='domain',
        ),
        migrations.RemoveField(
            model_name='offeryeardomain',
            name='offer_year',
        ),
        migrations.AlterUniqueTogether(
            name='offeryearentity',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='offeryearentity',
            name='education_group_year',
        ),
        migrations.RemoveField(
            model_name='offeryearentity',
            name='entity',
        ),
        migrations.RemoveField(
            model_name='offeryearentity',
            name='offer_year',
        ),
        migrations.RemoveField(
            model_name='structure',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='structure',
            name='part_of',
        ),
        migrations.RemoveField(
            model_name='structureaddress',
            name='country',
        ),
        migrations.RemoveField(
            model_name='structureaddress',
            name='structure',
        ),
        migrations.RemoveField(
            model_name='entitymanager',
            name='structure',
        ),
        migrations.RemoveField(
            model_name='learningunityear',
            name='structure',
        ),
        migrations.RemoveField(
            model_name='offerenrollment',
            name='offer_year',
        ),
        migrations.RemoveField(
            model_name='offeryearcalendar',
            name='offer_year',
        ),
        migrations.RemoveField(
            model_name='sessionexam',
            name='offer_year',
        ),
        migrations.AlterUniqueTogether(
            name='programmanager',
            unique_together={('person', 'education_group')},
        ),
        migrations.DeleteModel(
            name='ExternalOffer',
        ),
        migrations.DeleteModel(
            name='Offer',
        ),
        migrations.DeleteModel(
            name='OfferType',
        ),
        migrations.DeleteModel(
            name='OfferYearDomain',
        ),
        migrations.DeleteModel(
            name='OfferYearEntity',
        ),
        migrations.DeleteModel(
            name='Structure',
        ),
        migrations.DeleteModel(
            name='StructureAddress',
        ),
        migrations.RemoveField(
            model_name='programmanager',
            name='offer_year',
        ),
        migrations.DeleteModel(
            name='OfferYear',
        ),
    ]
