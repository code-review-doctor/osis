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
import mock
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpResponseForbidden
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.program_manager import ProgramManagerFactory
from program_management.ddd.domain.node import Node
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory


class TestSupprimerUnitesEnseignement(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.education_group_year = EducationGroupVersionFactory().offer
        cls.url = reverse('supprimer_unites_enseignement_view', kwargs={
            'annee': cls.education_group_year.academic_year.year,
            'code_programme': cls.education_group_year.partial_acronym,
            'code_groupement': cls.education_group_year.partial_acronym
        })

    def setUp(self) -> None:
        self.client.force_login(ProgramManagerFactory(
            education_group=self.education_group_year.education_group
        ).person.user)
        self.__mock_pgm_tree()

    def __mock_pgm_tree(self):
        program_tree_patcher = mock.patch(
            'program_management.ddd.repositories.program_tree.ProgramTreeRepository.get',
            return_value=ProgramTree(root_node=Node(code="A", children=[]))
        )
        contenu_pgm_patcher = mock.patch(
            'program_management.ddd.service.read.get_content_service._build_contenu_pgm',
        )
        program_tree_patcher.start()
        contenu_pgm_patcher.start()
        self.addCleanup(program_tree_patcher.stop)
        self.addCleanup(contenu_pgm_patcher.stop)

    def test_assert_access_denied(self):
        lambda_prgm_manager = ProgramManagerFactory()
        self.client.force_login(lambda_prgm_manager.person.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "preparation_inscription/supprimer_unites_enseignement.html")

    @mock.patch('infrastructure.utils.MessageBus.invoke')
    def test_post_to_delete_learning_units(self, mock_invoke):
        to_delete = ['A', 'B', 'C']
        response = self.client.post(self.url, data={'to_delete': to_delete})
        msg = next(msg for msg in get_messages(response.wsgi_request))
        self.assertEqual(msg.level, messages.SUCCESS)
        self.assertIn(', '.join(to_delete), msg.message)
