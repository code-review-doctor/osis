# Generated by Django 2.2.13 on 2021-01-05 09:32

from django.db import migrations, models
from django.db.models import Q


def copy_remarks_from_lu_to_luy(apps, schema_editor):
    LearningUnit = apps.get_model('base', 'LearningUnit')
    LearningUnitYear = apps.get_model('base', 'LearningUnitYear')
    lus = LearningUnit.objects.filter(
        Q(other_remark__isnull=False) | Q(faculty_remark__isnull=False)
    )
    for lu in lus:
        luys = lu.learningunityear_set.all()
        for luy in luys:
            if lu.faculty_remark:
                luy.faculty_remark = lu.faculty_remark
            elif lu.other_remark:
                luy.faculty_remark = lu.other_remark

        LearningUnitYear.objects.bulk_update(luys, ['faculty_remark'])


def adapt_initial_data_from_proposals(apps, schema_editor):
    ProposalLearningUnit = apps.get_model('base', 'ProposalLearningUnit')

    proposals = ProposalLearningUnit.objects.filter(
        Q(initial_data__learning_unit__other_remark__isnull=False) |
        Q(initial_data__learning_unit__faculty_remark__isnull=False)
    )
    for proposal in proposals:
        other_remark = proposal.initial_data['learning_unit']['other_remark']
        faculty_remark = proposal.initial_data['learning_unit']['faculty_remark']
        proposal.initial_data['learning_unit_year']['other_remark'] = other_remark
        proposal.initial_data['learning_unit_year']['faculty_remark'] = faculty_remark
        del proposal.initial_data['learning_unit']['other_remark']
        del proposal.initial_data['learning_unit']['faculty_remark']
    ProposalLearningUnit.objects.bulk_update(proposals, ['initial_data'])


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0549_auto_20201215_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningunityear',
            name='faculty_remark',
            field=models.TextField(blank=True, null=True, verbose_name='Faculty remark (unpublished)'),
        ),
        migrations.AddField(
            model_name='learningunityear',
            name='other_remark',
            field=models.TextField(blank=True, null=True, verbose_name='Other remark (intended for publication)'),
        ),
        migrations.RunPython(copy_remarks_from_lu_to_luy),
        migrations.RunPython(adapt_initial_data_from_proposals),
        migrations.RemoveField(
            model_name='learningunit',
            name='faculty_remark',
        ),
    ]
