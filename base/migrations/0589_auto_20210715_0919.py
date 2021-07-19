# Generated by Django 2.2.13 on 2021-07-15 09:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learning_unit', '0014_auto_20210604_1537'),
        ('base', '0588_remove_learningcomponentyear_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningunitenrollment',
            name='learning_class_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='learning_unit.LearningClassYear'),
        ),
        migrations.AlterUniqueTogether(
            name='learningunitenrollment',
            unique_together={('offer_enrollment', 'learning_unit_year', 'learning_class_year', 'enrollment_state')},
        ),
    ]
