# Generated by Django 2.2.13 on 2021-02-02 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learning_unit', '0005_role_migration_centralmanager_facultymanager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centralmanager',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_unit_centralmanager_set', to='base.Person'),
        ),
        migrations.AlterField(
            model_name='facultymanager',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_unit_facultymanager_set', to='base.Person'),
        ),
    ]
