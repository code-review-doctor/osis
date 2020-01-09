# Generated by Django 2.2.5 on 2020-01-09 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('education_group', '0003_groupyear_academic_year'),
        ('base', '0491_auto_20200107_1458'),
    ]

    operations = [
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('education_group_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.EducationGroupYear', verbose_name='education group year')),
                ('group_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='education_group.GroupYear', verbose_name='group year')),
                ('learning_class_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.LearningClassYear', verbose_name='learning class year')),
                ('learning_unit_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.LearningUnitYear', verbose_name='learning unit year')),
            ],
        ),
    ]
