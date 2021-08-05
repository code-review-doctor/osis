import csv
from typing import List, Tuple, Dict

from django.core.management.base import BaseCommand

from reference.models.continent import Continent
from reference.models.country import Country

COUNTRY_PATH = 'base/fixtures/countries.csv'


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.create_antarctica_continent()
        self.load_countries()

    @staticmethod
    def create_antarctica_continent() -> Continent:
        print("===== Getting or creating Antarctica continent ====\n")
        antarctica, _ = Continent.objects.get_or_create(
            code='AN',
            defaults={'name': "Antarctica"}
        )
        return antarctica

    def load_countries(self):
        created_countries, total = 0, 0
        print("===== Loading countries =====\n")
        with open(COUNTRY_PATH, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                iso_code, defaults_value = self._get_iso_code_and_default_values(row)
                country, created = Country.objects.update_or_create(
                    iso_code=iso_code,
                    defaults=defaults_value
                )
                if created:
                    created_countries += 1
                total += 1
                print("Country {country} {created_or_updated}".format(
                    country=country,
                    created_or_updated='created' if created else 'updated'
                ))

        print("\n===== {n_update} countries updated =====\n===== {n_create} countries created =====".format(
            n_update=total - created_countries,
            n_create=created_countries
        ))

        # print("===== {number} countries without name in english".format(
        #     number=Country.objects.filter(Q(name_en='') | Q(name_en__isnull=True)).count()
        # ))
        # print("===== {number} countries without continent".format(
        #     number=Country.objects.filter(continent_id__isnull=True).count()
        # ))
        # print("===== {number} countries without cref code".format(
        #     number=Country.objects.filter(cref_code__isnull=True).count()
        # ))

    @staticmethod
    def _get_iso_code_and_default_values(row: List[str]) -> Tuple[str, Dict[str, str]]:
        iso_code, name_fr, name_en, continent_code = row
        defaults_value = {
            'name': name_fr,
            'name_en': name_en,
        }
        if continent_code:
            defaults_value.update({
                'continent_id': Continent.objects.get(code=continent_code)
            })
        return iso_code, defaults_value
