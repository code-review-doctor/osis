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

import mock
from django.test import TestCase
from django.urls import reverse

from assessments.forms.score_encoding import ScoreEncodingProgressFilterForm
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from ddd.logic.encodage_des_notes.encodage.commands import GetCohortesGestionnaireCommand, GetPeriodeEncodageCommand
from ddd.logic.encodage_des_notes.shared_kernel.dtos import PeriodeEncodageNotesDTO, DateDTO


class ScoreEncodingProgressOverviewProgramManagerViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.program_manager = ProgramManagerFactory(person__global_id="123456789")
        cls.academic_year = AcademicYearFactory()

        cls.url = reverse('score_encoding_progress_overview')

    def setUp(self) -> None:
        self.client.force_login(self.program_manager.person.user)
        self.session_exam_calendar = SessionExamCalendarFactory.create_academic_event(self.academic_year)

        self.patch_message_bus = mock.patch(
            "assessments.views.program_manager.score_encoding_progress_overview.message_bus_instance.invoke",
            side_effect=self.__mock_message_bus_invoke
        )
        self.message_bus_mocked = self.patch_message_bus.start()
        self.addCleanup(self.patch_message_bus.stop)

    def __mock_message_bus_invoke(self, cmd):
        if isinstance(cmd, GetCohortesGestionnaireCommand):
            return []
        if isinstance(cmd, GetPeriodeEncodageCommand):
            return PeriodeEncodageNotesDTO(
                annee_concernee=2020,
                session_concernee=2,
                debut_periode_soumission=DateDTO.build_from_date(datetime.date.today() - datetime.timedelta(days=5)),
                fin_periode_soumission=DateDTO.build_from_date(datetime.date.today() + datetime.timedelta(days=16)),
            )
        raise Exception('Bus Command not mocked in test')

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_case_period_closed_assert_redirect_to_outside_period_view(self):
        self.session_exam_calendar.academic_calendar.delete()
        self.session_exam_calendar.delete()

        response = self.client.get(self.url)

        expected_redirect_url = reverse('outside_scores_encodings_period')
        self.assertRedirects(response, expected_redirect_url)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "assessments/program_manager/score_encoding_progress_overview.html")

    def test_assert_contexts(self):
        response = self.client.get(self.url)

        self.assertTrue('progression_generale' in response.context)
        self.assertTrue('last_synchronization' in response.context)
        self.assertEqual(response.context['person'], self.program_manager.person)
        self.assertIsInstance(response.context['periode_encodage'], PeriodeEncodageNotesDTO)
        self.assertIsInstance(response.context['search_form'], ScoreEncodingProgressFilterForm)

        expected_score_search_url = reverse('score_search')
        self.assertEqual(response.context['score_search_url'], expected_score_search_url)
