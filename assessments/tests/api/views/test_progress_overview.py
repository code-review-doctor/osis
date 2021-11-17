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
from types import SimpleNamespace

import mock
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from assessments.api.views.progress_overview import ProgressOverviewTutorView
from base.tests.factories.tutor import TutorFactory


class ProgressOverviewAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory()
        cls.url = reverse('assessments_api_v1:' + ProgressOverviewTutorView.name)

    def setUp(self):
        self.client.force_authenticate(user=self.tutor.person.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch('ddd.logic.encodage_des_notes.shared_kernel.domain.service.periode_encodage_ouverte.'
                'PeriodeEncodageOuverte.verifier')
    @mock.patch('ddd.logic.encodage_des_notes.soumission.domain.service.progression_generale_encodage.'
                'ProgressionGeneraleEncodage.get')
    def test_response(self, mock_get_progression, mock_periode_ouverte):
        mock_get_progression.return_value = SimpleNamespace(
            annee_academique=2020,
            numero_session=1,
            progression_generale=[SimpleNamespace(
                code_unite_enseignement='CODE',
                intitule_complet_unite_enseignement='Intitulé',
                dates_echeance=[],
                responsable_note=SimpleNamespace(nom='John', prenom='Doe'),
                a_etudiants_peps=False
            )]
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
