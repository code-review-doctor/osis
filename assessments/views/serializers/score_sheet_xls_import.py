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
import json

from django.utils.translation import gettext_lazy as _

from openpyxl.worksheet import Worksheet
from rest_framework import serializers

from assessments.business.score_encoding_export import HEADER


class ScoreSheetXLSImportSerializerError(ValueError):
    def __init__(self, message):
        self.message = message


class _XLSNoteEtudiantRowImportSerializer(serializers.Serializer):
    code_unite_enseignement = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    noma = serializers.SerializerMethodField()

    def get_code_unite_enseignement(self, obj: tuple):
        col_unite_enseignement = HEADER.index(_('Learning unit'))
        return obj[col_unite_enseignement].value

    def get_note(self, obj: tuple):
        col_note = HEADER.index(_('Numbered scores'))
        return str(obj[col_note].value) if obj[col_note].value else ''

    def get_email(self, obj: tuple):
        col_email = HEADER.index(_('Email'))
        return obj[col_email].value

    def get_noma(self, obj: tuple):
        col_noma = HEADER.index(_('Registration number'))
        return obj[col_noma].value


class ScoreSheetXLSImportSerializer(serializers.Serializer):
    numero_session = serializers.SerializerMethodField()
    annee_academique = serializers.SerializerMethodField()
    notes_etudiants = serializers.SerializerMethodField()

    def get_numero_session(self, worksheet: Worksheet) -> int:
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

    def __is_student_score_row(self, row) -> bool:
        col_registration_id = HEADER.index(_('Registration number'))
        raw_registration_id = row[col_registration_id].value
        return raw_registration_id and str(raw_registration_id).isdigit()

    def __get_student_rows(self, worksheet: Worksheet):
        return filter(self.__is_student_score_row, worksheet.rows)

    def __convert_to_integer(self, raw_cell_value) -> int:
        return int(raw_cell_value) if isinstance(raw_cell_value, str) and raw_cell_value.isdigit() else raw_cell_value

    def get_notes_etudiants(self, worksheet: Worksheet):
        notes_etudiants = []
        for count, row in enumerate(self.__get_student_rows(worksheet)):
            row_serialized = _XLSNoteEtudiantRowImportSerializer(instance=row).data
            notes_etudiants.append(row_serialized)
        return notes_etudiants

    def to_representation(self, instance):
        """
        Need in order to ensure backward compatibility with voluptuous library
        """
        representation = super().to_representation(instance)
        json_str = json.dumps(representation)
        return json.loads(json_str)
