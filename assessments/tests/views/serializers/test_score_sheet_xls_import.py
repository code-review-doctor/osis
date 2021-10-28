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
from typing import Union

from django.test import SimpleTestCase
from openpyxl import Workbook

from assessments.views.serializers.score_sheet_xls_import import ScoreSheetXLSImportSerializer, \
    ScoreSheetXLSImportSerializerError, ProgramManagerScoreSheetXLSImportSerializer


class ScoreSheetXLSImportSerializerTest(SimpleTestCase):
    def setUp(self) -> None:
        self.serializer_cls = ScoreSheetXLSImportSerializer
        self.workbook = Workbook()
        worksheet = self.workbook.active

        _add_row_to_worksheet(
            worksheet,
            13,
            annee_academique="2020-21",
            numero_session="2",
            code_cours="LEPL1509",
            noma="24641600",
            note="10",
            email="dummy@gmail.com",
        )

    def test_serialize_worksheet(self):
        score_sheet_serialized = self.serializer_cls(self.workbook.active).data

        self.assertEqual(score_sheet_serialized['annee_academique'], 2020)
        self.assertEqual(score_sheet_serialized['numero_session'], 2)

        self.assertEqual(len(score_sheet_serialized['notes_etudiants']), 1)
        self.assertEqual(score_sheet_serialized['notes_etudiants'][0]['code_unite_enseignement'],  "LEPL1509")
        self.assertEqual(score_sheet_serialized['notes_etudiants'][0]['note'], "10")
        self.assertEqual(score_sheet_serialized['notes_etudiants'][0]['email'], "dummy@gmail.com")
        self.assertEqual(score_sheet_serialized['notes_etudiants'][0]['noma'], "24641600")

    def test_assert_multiple_academic_year_found_raised_serialization_error(self):
        worksheet = self.workbook.active
        _add_row_to_worksheet(
            worksheet,
            14,
            annee_academique="2021-22",
            numero_session="2",
            code_cours="LEPL1509",
            noma="24641600",
            note="10",
            email="dummy@gmail.com",
        )

        with self.assertRaises(ScoreSheetXLSImportSerializerError):
            self.serializer_cls(self.workbook.active).data

    def test_assert_multiple_session_found_raised_serialization_error(self):
        worksheet = self.workbook.active
        _add_row_to_worksheet(
            worksheet,
            14,
            annee_academique="2020-21",
            numero_session="3",
            code_cours="LEPL1509",
            noma="24641600",
            note="10",
            email="dummy@gmail.com",
        )

        with self.assertRaises(ScoreSheetXLSImportSerializerError):
            self.serializer_cls(self.workbook.active).data

    def test_assert_serialize_zero_as_value(self):
        worksheet = self.workbook.active
        _add_row_to_worksheet(
            worksheet,
            13,
            annee_academique="2020-21",
            numero_session="2",
            code_cours="LEPL1509",
            noma="24641600",
            note=0,
            email="dummy@gmail.com",
        )

        serialized_data = self.serializer_cls(self.workbook.active).data
        self.assertEqual(serialized_data['notes_etudiants'][0]['note'], '0')

    def test_assert_convert_comma_to_dot(self):
        worksheet = self.workbook.active
        _add_row_to_worksheet(
            worksheet,
            13,
            annee_academique="2020-21",
            numero_session="2",
            code_cours="LEPL1509",
            noma="24641600",
            note="10,6",
            email="dummy@gmail.com",
        )
        serialized_data = self.serializer_cls(self.workbook.active).data
        self.assertEqual(serialized_data['notes_etudiants'][0]['note'], '10.6')


class ProgramManagerScoreSheetXLSImportSerializerTest(SimpleTestCase):
    def setUp(self) -> None:
        self.workbook = Workbook()
        self.serializer_cls = ProgramManagerScoreSheetXLSImportSerializer

    def test_assert_A_letter_transformed_to_S_letter(self):
        worksheet = self.workbook.active

        _add_row_to_worksheet(
            worksheet,
            13,
            annee_academique="2020-21",
            numero_session="2",
            code_cours="LEPL1509",
            noma="24641600",
            note="A",
            email="dummy@gmail.com",
        )
        serialized_data = self.serializer_cls(self.workbook.active).data
        self.assertEqual(serialized_data['notes_etudiants'][0]['note'], 'S')


def _add_row_to_worksheet(
        worksheet,
        row_number,
        annee_academique: str,
        numero_session: str,
        code_cours: str,
        noma: str,
        note: Union[str, int],
        email: str
):
    worksheet['A' + str(row_number)].value = annee_academique
    worksheet['B' + str(row_number)].value = numero_session
    worksheet['C' + str(row_number)].value = code_cours
    worksheet['E' + str(row_number)].value = noma
    worksheet['I' + str(row_number)].value = note
    worksheet['H' + str(row_number)].value = email
