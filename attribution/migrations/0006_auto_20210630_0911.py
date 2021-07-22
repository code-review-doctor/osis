# Generated by Django 2.2.13 on 2021-06-30 09:11

import uuid

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def create_uuid(apps, schema_editor):
    AttributionNew = apps.get_model('attribution', 'AttributionNew')
    attributions = AttributionNew.objects.all()
    for attribution in attributions:
        attribution.uuid = uuid.uuid4()
    AttributionNew.objects.bulk_update(attributions, ['uuid'], batch_size=1000)


class Migration(migrations.Migration):

    dependencies = [
        ('learning_unit', '0014_auto_20210604_1537'),
        ('attribution', '0005_auto_20210617_1727'),
    ]

    operations = [
        migrations.AddField(
            model_name='attributionnew',
            name='uuid',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.RunPython(create_uuid),
        migrations.AlterField(
            model_name='attributionnew',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
        ),
        migrations.CreateModel(
            name='AttributionClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('allocation_charge', models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True,
                                                          validators=[django.core.validators.MinValueValidator(0)])),
                ('attribution_charge',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attribution.AttributionChargeNew')),
                ('learning_class_year',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning_unit.LearningClassYear')),
            ],
        ),
    ]
