import csv

from django.core.management.base import BaseCommand

from reference.models.country import Country

CSV_PATH = 'base/fixtures/countries.csv'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--iso_position', nargs='+', type=int)
        parser.add_argument('--fr_position', nargs='+', type=int)
        parser.add_argument('--en_position', nargs='+', type=int)

    def handle(self, *args, **kwargs):
        iso_position = kwargs.get('iso_position', 2)
        fr_position = kwargs.get('fr_position', 4)
        en_position = kwargs.get('en_position', 5)
        self.load_countries(iso_position, fr_position, en_position)

    @staticmethod
    def load_countries(iso_position: int, fr_position: int, en_position: int):
        created_countries, total = 0, 0
        print("===== Loading countries =====\n")
        with open(CSV_PATH, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                iso_code = row[iso_position]
                name_fr = row[fr_position]
                name_en = row[en_position]
                country, created = Country.objects.update_or_create(
                    iso_code=iso_code,
                    defaults={
                        'name': name_fr,
                        'name_en': name_en
                    }
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
