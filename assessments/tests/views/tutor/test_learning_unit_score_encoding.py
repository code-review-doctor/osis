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
import mock
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from base.tests.factories.tutor import TutorFactory
from ddd.logic.encodage_des_notes.shared_kernel.dtos import FeuilleDeNotesDTO, EnseignantDTO, DetailContactDTO
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand, GetResponsableDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.dtos import ResponsableDeNotesDTO


class LearningUnitScoreEncodingTutorViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory(person__global_id="123456789")
        cls.academic_year = AcademicYearFactory()

        cls.url = reverse('learning_unit_score_encoding', kwargs={
            'learning_unit_code': 'LEPL1509'
        })

    def setUp(self) -> None:
        self.client.force_login(self.tutor.person.user)
        self.session_exam_calendar = SessionExamCalendarFactory.create_academic_event(self.academic_year)

        self.patch_message_bus = mock.patch(
            "assessments.views.tutor.learning_unit_score_encoding.message_bus_instance.invoke",
            side_effect=self.__mock_message_bus_invoke
        )
        self.message_bus_mocked = self.patch_message_bus.start()
        self.addCleanup(self.patch_message_bus.stop)

    def __mock_message_bus_invoke(self, cmd):
        if isinstance(cmd, GetFeuilleDeNotesCommand):
            return FeuilleDeNotesDTO(
                code_unite_enseignement='LEPL1509',
                intitule_complet_unite_enseignement='Introduction au data-mining',
                note_decimale_est_autorisee=True,
                responsable_note=EnseignantDTO(nom="Durant", prenom="Thomas"),
                contact_responsable_notes=DetailContactDTO(
                    matricule_fgs="987654321",
                    email="thomas.durant@email.be",
                    adresse_professionnelle=None,
                    langue="fr-be"
                ),
                autres_enseignants=[],
                annee_academique=2020,
                numero_session=2,
                notes_etudiants=[],
            )
        if isinstance(cmd, GetResponsableDeNotesCommand):
            return ResponsableDeNotesDTO(
                nom="Durant",
                prenom="Thomas",
                matricule='78965432',
                code_unite_enseignement='LEPL1509',
                annee_unite_enseignement=2020,
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

        self.assertTemplateUsed(response, "assessments/tutor/learning_unit_score_encoding.html")

    def test_assert_contexts(self):
        response = self.client.get(self.url)

        self.assertIsInstance(response.context['learning_unit_encoding_url'], str)
        self.assertIsInstance(response.context['learning_unit_print_url'], str)
        self.assertIsInstance(response.context['learning_unit_download_xls_url'], str)
        self.assertIsInstance(response.context['learning_unit_upload_xls_url'], str)
        self.assertIsInstance(response.context['learning_unit_submit_url'], str)
        self.assertIsInstance(response.context['can_submit_scores'], bool)
        self.assertIsInstance(response.context['feuille_de_notes'], FeuilleDeNotesDTO)
