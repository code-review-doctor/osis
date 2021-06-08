# Generated by Django 2.2.5 on 2020-01-08 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0496_auto_20200106_1543'),
    ]

    def empty_code_name_to_none(apps, schema_editor):
        learning_achievement_model = apps.get_model("base", "LearningAchievement")
        learning_achievement_model.objects.filter(
            code_name__in=['.', '']
        ).update(
            code_name=None
        )

    def fill_null_code_name(apps, schema_editor):
        learning_achievement_model = apps.get_model("base", "LearningAchievement")
        learning_achievement_model.objects.filter(
            code_name=None
        ).update(
            code_name='.'
        )

    operations = [
        migrations.AlterField(
            model_name='learningachievement',
            name='code_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='code'),
        ),
        migrations.RunPython(empty_code_name_to_none, reverse_code=fill_null_code_name, elidable=True)
    ]
