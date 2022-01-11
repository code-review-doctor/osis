#!/usr/bin/env python
from openpyxl import load_workbook

from django.core.management.base import BaseCommand
from base.models.learning_unit_year import LearningUnitYear

CODE_TITLE = "Code"
YEAR_TITLE = "Anac."
ENGLISH_FRIENDLY_TITLE = "English-friendly"
FRENCH_FRIENDLY_TITLE = "French-friendly"
EXCHANGE_STUDENTS_TITLE = "Etudiants d'échange"


class Command(BaseCommand):
    def handle(self, *args, **options):
        workbook = load_workbook("mobility_ues.xlsx", read_only=True, data_only=True)
        ws = workbook.worksheets[0]

        xls_rows = list(ws.rows)
        cols_references = {}
        for idx, cell in enumerate(xls_rows[0]):
            cols_references.update({cell.value: idx})

        mandatory_titles = {
            CODE_TITLE,
            YEAR_TITLE,
            ENGLISH_FRIENDLY_TITLE,
            FRENCH_FRIENDLY_TITLE,
            EXCHANGE_STUDENTS_TITLE
        }

        nb_xls_lines_treated = 0
        nb_of_distinct_acronyms_treated = 0
        if self._check_columns_ok(cols_references, mandatory_titles):
            for line_index, row in enumerate(xls_rows[1:], 2):
                if row[cols_references.get(CODE_TITLE)].value:
                    acronym = row[cols_references.get(CODE_TITLE)].value.strip()
                    year = row[cols_references.get(YEAR_TITLE)].value[0:4]
                    if not year.isdigit() or int(year) < 2000 or int(year) > 2999:
                        self.stderr.write("Unexpected year value : {}".format(year))

                    mobility_ues = LearningUnitYear.objects.filter(
                        acronym__iexact=acronym,
                        academic_year__year__gte=year
                    )
                    if mobility_ues:
                        nb_of_distinct_acronyms_treated += 1
                        for ue in mobility_ues:
                            # self.stdout.write("Learning unit year modified : {}/{}".format(
                            #     ue.acronym,
                            #     ue.academic_year.year)
                            # )
                            ue.english_friendly = self._get_boolean_value(
                                row[cols_references.get(ENGLISH_FRIENDLY_TITLE)].value,
                                line_index,
                                ENGLISH_FRIENDLY_TITLE
                            )
                            ue.french_friendly = self._get_boolean_value(
                                row[cols_references.get(FRENCH_FRIENDLY_TITLE)].value,
                                line_index,
                                FRENCH_FRIENDLY_TITLE
                            )
                            ue.exchange_students = self._get_boolean_value(
                                row[cols_references.get(EXCHANGE_STUDENTS_TITLE)].value,
                                line_index,
                                EXCHANGE_STUDENTS_TITLE
                            )
                            ue.save()
                    else:
                        self.stderr.write(
                            "No learning unit corresponding to the acronym : '{}'. Corresponds to Xls line {}".format(
                                acronym, line_index
                            )
                        )
                    nb_xls_lines_treated += 1

        self.stdout.write("Number of xls line treated : {}".format(nb_xls_lines_treated))
        self.stdout.write("Number of distinct acronym treated : {}".format(nb_of_distinct_acronyms_treated))

    def _check_columns_ok(self, cols_references, mandatory_titles):
        for title in mandatory_titles:
            if title not in cols_references:
                self.stderr.write("Mandatory column(s) is(are) missing : {}".format(title))
                raise SystemExit(1)
        return True

    def _get_boolean_value(self, value, line_index, column_title):
        value_to_convert = None
        if value:
            value_to_convert = value.strip().lower()
        if value_to_convert == "oui":
            return True
        elif value_to_convert == "non":
            return False
        else:
            self.stderr.write("Unexpected value : '{}'! Corresponds to Xls line {}, column '{}'".format(value, line_index, column_title))
            raise SystemExit(1)
