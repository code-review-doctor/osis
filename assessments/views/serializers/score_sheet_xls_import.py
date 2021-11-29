##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import decimal
import json
from typing import List

from django.utils.translation import gettext_lazy as _, pgettext_lazy
from openpyxl.worksheet import Worksheet
from rest_framework import serializers
from assessments.export.score_sheet_xls import HEADER
from ddd.logic.encodage_des_notes.encodage.domain.validator.exceptions import NoteIncorrecteException

MAXIMAL_NUMBER_OF_DECIMALS = 1


class ScoreSheetXLSImportSerializerError(ValueError):
    def __init__(self, message):
        self.message = message


class _XLSNoteEtudiantRowImportSerializer(serializers.Serializer):
    code_unite_enseignement = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    noma = serializers.SerializerMethodField()
    row_number = serializers.SerializerMethodField()

    @staticmethod
    def get_code_unite_enseignement(obj: tuple) -> str:
        col_unite_enseignement = HEADER.index(_('Learning unit'))
        return str(obj[col_unite_enseignement].value)

    def get_note(self, obj: tuple) -> str:
        col_note = HEADER.index(_('Score'))
        raw_value = str(obj[col_note].value) if obj[col_note].value is not None else ''
        note_value = raw_value.replace(",", ".")
        number_of_decimal = decimal.Decimal(note_value).as_tuple().exponent * -1
        if number_of_decimal > MAXIMAL_NUMBER_OF_DECIMALS:
            raise ScoreSheetXLSImportSerializerError(
                _('Invalid score line %(row_number)s : %(decimal_value)s. Ensure that there are no more '
                  'than %(max_decimal)s decimal place.') %
                {
                    'decimal_value': note_value,
                    'max_decimal': MAXIMAL_NUMBER_OF_DECIMALS,
                    'row_number': str(self.get_row_number(obj))
                }
            )

        return note_value

    @staticmethod
    def get_email(obj: tuple) -> str:
        col_email = HEADER.index(_('Email'))
        return str(obj[col_email].value)

    @staticmethod
    def get_noma(obj: tuple) -> str:
        col_noma = HEADER.index(pgettext_lazy('assessments', 'Registration number'))
        return str(obj[col_noma].value)

    def get_row_number(self, obj: tuple) -> int:
        return self.context['row_number']


class ScoreSheetXLSImportSerializer(serializers.Serializer):
    numero_session = serializers.SerializerMethodField()
    annee_academique = serializers.SerializerMethodField()
    notes_etudiants = serializers.SerializerMethodField()

    def get_numero_session(self, worksheet: Worksheet) -> int:
        self._check_headers_consistency(worksheet)

        col_session = HEADER.index(_('Session'))
        session_found = set()
        for count, row in enumerate(self.__get_student_rows(worksheet)):
            raw_session_value = row[col_session].value
            session_cleaned = self.__convert_to_integer(raw_session_value)
            session_found.add(session_cleaned)

        if len(session_found) == 0:
            raise ScoreSheetXLSImportSerializerError(
                _("File error : No value in the column Session. No scores injected."),
            )
        elif len(session_found) > 1:
            raise ScoreSheetXLSImportSerializerError(
                _("File error : Different values in the column Session. No scores injected."),
            )
        return session_found.pop()

    def get_annee_academique(self, worksheet: Worksheet) -> int:
        col_academic_year = HEADER.index(_('Academic year'))
        academic_year_found = set()

        for count, row in enumerate(self.__get_student_rows(worksheet)):
            raw_academic_year_value = row[col_academic_year].value[:4]
            academic_year_cleaned = self.__convert_to_integer(raw_academic_year_value)
            academic_year_found.add(academic_year_cleaned)

        # TODO: Make translation as normal
        if len(academic_year_found) == 0:
            raise ScoreSheetXLSImportSerializerError(
                _("no_valid_academic_year_error"),
            )
        elif len(academic_year_found) > 1:
            raise ScoreSheetXLSImportSerializerError(
                _("more_than_one_academic_year_error"),
            )
        return academic_year_found.pop()

    @staticmethod
    def __is_student_score_row(row) -> bool:
        col_registration_id = HEADER.index(pgettext_lazy('assessments', 'Registration number'))
        raw_registration_id = row[col_registration_id].value
        return raw_registration_id and str(raw_registration_id).isdigit()

    def __get_student_rows(self, worksheet: Worksheet):
        return filter(self.__is_student_score_row, worksheet.rows)

    @staticmethod
    def __convert_to_integer(raw_cell_value) -> int:
        try:
            return int(raw_cell_value)
        except (ValueError, TypeError,):
            return raw_cell_value

    def get_notes_etudiants(self, worksheet: Worksheet) -> List[_XLSNoteEtudiantRowImportSerializer]:
        notes_etudiants = []
        for row in self.__get_student_rows(worksheet):
            row_serialized = _XLSNoteEtudiantRowImportSerializer(instance=row, context={'row_number': row[0].row}).data
            notes_etudiants.append(row_serialized)
        return notes_etudiants

    def to_representation(self, instance):
        """
        Need in order to ensure backward compatibility with voluptuous library
        """
        representation = super().to_representation(instance)
        json_str = json.dumps(representation)
        return json.loads(json_str)

    @staticmethod
    def _check_headers_consistency(worksheet):
        headers_line_found = False
        for count, row in enumerate(worksheet.rows):
            if row[0].value == HEADER[0]:
                headers_line_found = True
                for header_count, header in enumerate(HEADER):
                    try:
                        if row[header_count].value != header:
                            raise ScoreSheetXLSImportSerializerError(
                                _("File error : The file is not consistent. No scores injected."),
                            )
                    except Exception as e:
                        raise ScoreSheetXLSImportSerializerError(
                            _("File error : The file is not consistent. No scores injected."),
                        )
                break
        if not headers_line_found:
            raise ScoreSheetXLSImportSerializerError(
                _("File error : The file is not consistent. No scores injected."),
            )


class ProgramManagerScoreSheetXLSImportSerializer(ScoreSheetXLSImportSerializer):
    def get_notes_etudiants(self, worksheet: Worksheet):
        notes_etudiants = []
        for row in super().get_notes_etudiants(worksheet):
            if row['note'] in ["A", "a"]:
                row['note'] = "S"
            notes_etudiants.append(row)
        return notes_etudiants
