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
import datetime
from unittest.mock import patch

from django.test import SimpleTestCase

from assessments.calendar.scores_exam_submission_calendar import ScoresExamSubmissionCalendar
from base.business.academic_calendar import AcademicSessionEvent
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from ddd.logic.encodage_des_notes.soumission.dtos import PeriodeSoumissionNotesDTO, DateDTO
from infrastructure.encodage_de_notes.soumission.domain.service.periode_encodage_notes import \
    PeriodeEncodageNotesTranslator


@patch.object(ScoresExamSubmissionCalendar, 'get_opened_academic_events')
class PeriodeSoumissionNotesTest(SimpleTestCase):

    def setUp(self):
        self.annee_concernee = 2020
        self.translator = PeriodeEncodageNotesTranslator()

    def test_should_renvoyer_aucune_periode_trouvee(self, mock_opened_events):
        mock_opened_events.return_value = []
        self.assertIsNone(self.translator.get())

    def test_should_renvoyer_periode_fermee(self, mock_opened_events):
        hier = datetime.date.today() - datetime.timedelta(days=1)
        periode_fermee = AcademicSessionEvent(
            id=1,
            title="Periode de soumission des notes session 2",
            authorized_target_year=self.annee_concernee,
            start_date=hier,
            end_date=hier,
            type=AcademicCalendarTypes.SCORES_EXAM_SUBMISSION.name,
            session=2,
        )
        mock_opened_events.return_value = [periode_fermee]
        expected_result = PeriodeSoumissionNotesDTO(
            annee_concernee=self.annee_concernee,
            session_concernee=2,
            debut_periode_soumission=DateDTO(jour=hier.day, mois=hier.month, annee=hier.year),
            fin_periode_soumission=DateDTO(jour=hier.day, mois=hier.month, annee=hier.year),
        )
        self.assertEqual(expected_result, self.translator.get())

    def test_should_renvoyer_periode_ouverte(self, mock_opened_events):
        aujourdhui = datetime.date.today()
        periode_fermee = AcademicSessionEvent(
            id=1,
            title="Periode de soumission des notes session 2",
            authorized_target_year=self.annee_concernee,
            start_date=aujourdhui,
            end_date=aujourdhui,
            type=AcademicCalendarTypes.SCORES_EXAM_SUBMISSION.name,
            session=2,
        )
        mock_opened_events.return_value = [periode_fermee]
        expected_result = PeriodeSoumissionNotesDTO(
            annee_concernee=self.annee_concernee,
            session_concernee=2,
            debut_periode_soumission=DateDTO(jour=aujourdhui.day, mois=aujourdhui.month, annee=aujourdhui.year),
            fin_periode_soumission=DateDTO(jour=aujourdhui.day, mois=aujourdhui.month, annee=aujourdhui.year),
        )
        self.assertEqual(expected_result, self.translator.get())
