##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.http.response import HttpResponseForbidden
from django.test import TestCase
from django.urls import reverse
from mock import mock

from base.tests.factories.person import PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from ddd.logic.preparation_programme_annuel_etudiant.dtos import ProgrammeInscriptionCoursDTO
from preparation_inscription.views.program_tree import ProgramTreeHTMLView
from program_management.ddd.domain.program_tree_version import STANDARD


class TestProgramTreeView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse(
            ProgramTreeHTMLView.name,
            kwargs={'annee': 2022, 'code_programme': 'LCORP201S'}
        )

    def setUp(self) -> None:
        pgm_manager = ProgramManagerFactory()
        self.client.force_login(pgm_manager.person.user)
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch(
            'infrastructure.messages_bus.get_programme_inscription_cours',
            return_value=ProgrammeInscriptionCoursDTO(
                uuid='aa0d2466-e013-4038-9c0d-6a8c726c4f88',
                code='LCORP201S',
                annee=2022,
                version=STANDARD,
                intitule_complet_formation='Master [120] en communication',
                sous_programme=[]
            )
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

    def test_user_has_not_permission(self):
        person_without_permission = PersonFactory()
        self.client.force_login(person_without_permission.user)

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "preparation_inscription/blocks/tree_recursif.html")
