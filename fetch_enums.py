import csv
import itertools
from typing import Iterable, List

import attr
import django.apps
from django.conf import settings
from django.db.models import CharField
from django.utils import translation

FRENCH = settings.LANGUAGE_CODE_FR
ENGLISH = settings.LANGUAGE_CODE_EN


@attr.s(frozen=True, slots=True)
class FieldChoice:
    app_label = attr.ib(type=str)
    model_name = attr.ib(type=str)
    db_table_name = attr.ib(type=str)
    field_name = attr.ib(type=str)
    db_value = attr.ib(type=str)
    fr_trans = attr.ib(type=str)
    en_trans = attr.ib(type=str)


def get_choices() -> Iterable['FieldChoice']:
    all_models = django.apps.apps.get_models()
    for model in all_models:
        charfields = [field for field in model._meta.fields if isinstance(field, CharField)]
        for field in charfields:
            for choice in field.choices:
                key = choice[0]

                with translation.override(FRENCH):
                    fr_trans = str(choice[1])

                with translation.override(ENGLISH):
                    en_trans = str(choice[1])

                yield FieldChoice(
                    app_label=model._meta.app_label,
                    model_name=model._meta.model_name,
                    db_table_name=model._meta.db_table,
                    field_name=field.name,
                    db_value=key,
                    fr_trans=fr_trans,
                    en_trans=en_trans
                )


def format_choices_for_csv(choices: Iterable['FieldChoice']) -> List:
    csv_rows = [
        (choice.db_table_name, choice.field_name, choice.db_value, choice.en_trans, choice.fr_trans)
        for choice in choices
    ]

    return sorted(
        csv_rows,
        key=lambda row: (row[0], row[1], row[2])
    )


def save_csv(choices: Iterable[(FieldChoice)]) -> None:
    csv_rows = format_choices_for_csv(choices)

    with open('enums.csv', 'w', newline='') as csvfile:
        enumcsv = csv.writer(csvfile, delimiter=',')
        enumcsv.writerows(csv_rows)


def generate_csv():
    choices = get_choices()
    save_csv(choices)
