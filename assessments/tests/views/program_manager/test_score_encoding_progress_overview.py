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
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from base.tests.factories.user import UserFactory
from ddd.logic.encodage_des_notes.encodage.commands import GetCohortesGestionnaireCommand, GetPeriodeEncodageCommand
from ddd.logic.encodage_des_notes.shared_kernel.dtos import PeriodeEncodageNotesDTO, DateDTO
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory


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


class RechercheCodeUeEtClasseAutocompleteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.year = 2020
        cls.user = UserFactory()
        cls.url = reverse('learning-unit-code-autocomplete')

    def setUp(self) -> None:
        self.patch_message_bus = mock.patch(
            "assessments.views.program_manager.score_encoding_progress_overview.message_bus_instance.invoke",
            side_effect=self.__mock_message_bus_invoke
        )
        self.message_bus_mocked = self.patch_message_bus.start()
        self.addCleanup(self.patch_message_bus.stop)

    def __mock_message_bus_invoke(self, cmd):
        if isinstance(cmd, GetPeriodeEncodageCommand):
            aujourdhui = datetime.date.today()
            return PeriodeEncodageNotesDTO(
                annee_concernee=self.year,
                session_concernee=1,
                debut_periode_soumission=aujourdhui,
                fin_periode_soumission=aujourdhui,
            )

    def test_should_be_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'q': 'existepas'})
        results = response.json()['results']
        self.assertEqual(len(results), 0)

    def test_should_rien_trouver_en_dessous_3_chars(self):
        LearningClassYearFactory(
            learning_component_year__learning_unit_year__academic_year__year=self.year,
            learning_component_year__learning_unit_year__acronym='LDROI1234',
            learning_component_year__type=LECTURING,
            acronym='F',
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'q': 'LD'})
        results = response.json()['results']
        self.assertEqual(len(results), 1)
        response = self.client.get(self.url, {'q': 'LDR'})
        results = response.json()['results']
        self.assertEqual(len(results), 3)

    def test_should_trouver_une_classe_magistrale(self):
        LearningClassYearFactory(
            learning_component_year__learning_unit_year__academic_year__year=self.year,
            learning_component_year__learning_unit_year__acronym='LDROI1234',
            learning_component_year__type=LECTURING,
            acronym='F',
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'q': 'LDROI1234-F'})
        results = response.json()['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'LDROI1234-F')

    def test_should_trouver_une_unite_enseignement(self):
        LearningUnitYearFactory(
            academic_year__year=self.year,
            acronym='LDROI1234',
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'q': 'LDROI1234'})
        results = response.json()['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'LDROI1234')

    def test_should_trouver_une_classe_pratique(self):
        LearningClassYearFactory(
            learning_component_year__learning_unit_year__academic_year__year=self.year,
            learning_component_year__learning_unit_year__acronym='LDROI1234',
            learning_component_year__type=PRACTICAL_EXERCISES,
            acronym='F',
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'q': 'LDROI1234_F'})
        results = response.json()['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'LDROI1234_F')

    def test_should_trouver_recherche_encodee_dans_resultat(self):
        LearningClassYearFactory(
            learning_component_year__learning_unit_year__academic_year__year=self.year,
            learning_component_year__learning_unit_year__acronym='LDROI1234',
            learning_component_year__type=PRACTICAL_EXERCISES,
            acronym='F',
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'q': 'LDROI1'})
        results = response.json()['results']
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['text'], 'LDROI1')  # partestam de recherche
        self.assertEqual(results[1]['text'], 'LDROI1234')  # unité enseignement
        self.assertEqual(results[2]['text'], 'LDROI1234_F')  # classe

    def test_should_ignorer_recherche_dans_resultat_si_aucune_ue_ou_classe_trouvee(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'q': 'LEXISTEPAS'})
        results = response.json()['results']
        self.assertEqual(len(results), 0)
