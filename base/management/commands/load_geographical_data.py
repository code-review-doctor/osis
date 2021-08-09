import csv
from typing import List, Tuple, Dict

from django.core.management.base import BaseCommand
from django.db.models import Q

from reference.models.continent import Continent
from reference.models.country import Country
from reference.models.zipcode import ZipCode

PATH = 'base/fixtures/{file_name}'
COUNTRY_FILE = 'countries.csv'
ZIPCODE_FILE = 'zipcode.csv'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--debug', nargs='?', default=False, type=bool)
        parser.add_argument('--countries', nargs='?', default=True)
        parser.add_argument('--zipcodes', nargs='?', default=True)

    def handle(self, *args, **kwargs):
        debug = kwargs['debug']
        if kwargs['countries'] is True:
            self.create_antarctica_continent()
            self.load_countries(debug)
        if kwargs['zipcodes'] is True:
            self.load_zipcodes()

    @staticmethod
    def create_antarctica_continent() -> Continent:
        print("===== Getting or creating Antarctica continent ====\n")
        antarctica, _ = Continent.objects.get_or_create(
            code='AN',
            defaults={'name': "Antarctica"}
        )
        return antarctica

    def load_countries(self, debug: bool):
        created_countries, total = 0, 0
        print("===== Loading countries =====\n")
        country_path = PATH.format(file_name=COUNTRY_FILE)
        with open(country_path, newline='') as csvfile:
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
        if debug:
            print("===== {number} countries without name in english".format(
                number=Country.objects.filter(Q(name_en='') | Q(name_en__isnull=True)).count()
            ))
            print("===== {number} countries without continent".format(
                number=Country.objects.filter(continent_id__isnull=True).count()
            ))
            print("===== {number} countries without cref code".format(
                number=Country.objects.filter(cref_code__isnull=True).count()
            ))

    @staticmethod
    def _get_iso_code_and_default_values(row: List[str]) -> Tuple[str, Dict[str, str]]:
        iso_code, name_fr, name_en, continent_code = row
        defaults_value = {
            'name': name_fr,
            'name_en': name_en,
        }
        if continent_code:
            defaults_value.update({
                'continent_id': Continent.objects.get(code=continent_code).id
            })
        return iso_code, defaults_value

    @staticmethod
    def load_zipcodes():
        zip_to_create = []
        print("===== Loading zip codes =====\n")
        zip_path = PATH.format(file_name=ZIPCODE_FILE)
        with open(zip_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                zip_code, municipality, country_code = row
                zip_object = ZipCode(
                    zip_code=zip_code,
                    municipality=municipality,
                    country_id=Country.objects.get(iso_code=country_code)
                )
                print("Creating Zipcode {zip}".format(zip=zip_object))
                zip_to_create.append(zip_object)
        ZipCode.objects.bulk_create(zip_to_create, batch_size=1000)
        print("\n===== {n} zipcodes created =====".format(n=len(zip_to_create)))
