# Generated by Django 2.2.13 on 2021-08-03 09:47

import csv
from typing import List

from django.db import migrations, models


def run_script(apps, schema_editor):
    Country = apps.get_model('reference', 'Country')
    countries_to_update, countries_to_create = [], []
    unknown_countries = 0
    print("===== Starting updating name_en or creating countries =====\n")
    with open('sql-pays.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            try:
                countries_to_update.append(
                    _edit_country_title_en(Country, row)
                )
            except Country.DoesNotExist:
                unknown_countries += 1
                countries_to_create.append(
                    _create_new_country(Country, row)
                )

    Country.objects.bulk_update(countries_to_update, ['name_en'], batch_size=1000)
    Country.objects.bulk_create(countries_to_create, batch_size=1000)

    print("\n=== {n_update} countries updated ===\n=== {n_add} countries added ===".format(
        n_update=len(countries_to_update),
        n_add=unknown_countries
    ))


def _create_new_country(country_model, row: List[str]):
    _, _, iso_code, _, name_fr, name_en = row
    print(
        "==================== "
        "Country doesn't exist in OSIS ==> Creating it : {iso_code} : {name_fr} - {name_en}"
        " ====================".format(
            iso_code=iso_code,
            name_fr=name_fr,
            name_en=name_en
        )
    )
    new_country = country_model(
        name=name_fr,
        name_en=name_en,
        iso_code=iso_code
    )
    return new_country


def _edit_country_title_en(country_model, row: List[str]):
    _, _, iso_code, _, name_fr, name_en = row
    print("Adding title_en {name_en} to {name_fr}".format(
        name_fr=name_fr,
        name_en=name_en
    ))
    country = country_model.objects.get(iso_code=iso_code)
    country.name_en = name_en
    return country


class Migration(migrations.Migration):
    dependencies = [
        ('reference', '0006_auto_20210623_0902'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='name_en',
            field=models.CharField(blank=True, max_length=80, unique=True, null=True),
        ),
        migrations.RunPython(run_script),
        migrations.AlterField(
            model_name='country',
            name='name_en',
            field=models.UUIDField(blank=True, max_length=80, unique=True)
        ),
    ]
