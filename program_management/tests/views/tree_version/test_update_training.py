# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import mock
from django.http import HttpResponseForbidden, HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.tests.factories.person import PersonFactory
from education_group.ddd.domain.group import GroupIdentity
from education_group.ddd.factories.group import GroupFactory
from education_group.tests.ddd.factories.training import TrainingFactory
from education_group.tests.factories.auth.central_manager import CentralManagerFactory
from education_group.tests.factories.group_year import GroupYearFactory as GroupYearDBFactory
from program_management.forms.version import UpdateTrainingVersionForm
from program_management.tests.ddd.factories.program_tree_version import SpecificProgramTreeVersionFactory, \
    StandardProgramTreeVersionFactory


class TestTrainingVersionUpdateGetView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.training_version_obj = SpecificProgramTreeVersionFactory()
        cls.group_obj = GroupFactory(
            entity_identity=GroupIdentity(
                code=cls.training_version_obj.tree.root_node.code,
                year=cls.training_version_obj.tree.root_node.year
            )
        )
        cls.training_obj = TrainingFactory()

        cls.url = reverse(
            'training_version_update',
            kwargs={"code": cls.group_obj.code, "year": cls.group_obj.year}
        )

        # Create db data for permission
        group_year_db = GroupYearDBFactory(partial_acronym=cls.group_obj.code, academic_year__year=cls.group_obj.year,)
        cls.central_manager = CentralManagerFactory(entity=group_year_db.management_entity)

    def setUp(self):
        self.client.force_login(self.central_manager.person.user)

        # Mock for service
        self.get_group_patcher = mock.patch(
            "program_management.views.tree_version.update_training.get_group_service.get_group",
            return_value=self.group_obj
        )
        self.mocked_get_group = self.get_group_patcher.start()
        self.addCleanup(self.get_group_patcher.stop)

        self.get_training_patcher = mock.patch(
            "program_management.views.tree_version.update_training.get_training_service.get_training",
            return_value=self.training_obj
        )
        self.mocked_get_training = self.get_training_patcher.start()
        self.addCleanup(self.get_training_patcher.stop)

        self.get_training_version_patcher = mock.patch(
            "program_management.views.tree_version.update_training."
            "get_program_tree_version_from_node_service.get_program_tree_version_from_node",
            return_value=self.training_version_obj
        )
        self.mocked_get_training_version = self.get_training_version_patcher.start()
        self.addCleanup(self.get_training_version_patcher.stop)

    def test_case_when_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_when_user_has_no_permission(self):
        a_person_without_permission = PersonFactory()
        self.client.force_login(a_person_without_permission.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_when_url_is_a_standard_version_assert_redirect(self):
        standard_version = StandardProgramTreeVersionFactory()
        self.mocked_get_training_version.return_value = standard_version
        self.mocked_get_group.return_value = standard_version.tree.root_node

        url = reverse(
            'training_version_update',
            kwargs={
                "code": standard_version.tree.root_node.code,
                "year": standard_version.tree.root_node.year
            }
        )

        response = self.client.get(url)
        expected_redirect = reverse('training_update', kwargs={
            'year': standard_version.tree.root_node.year,
            'code': standard_version.tree.root_node.code,
            'title': self.training_obj.acronym
        })
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    @mock.patch('program_management.forms.version.get_end_postponement_year_service.'
                'calculate_program_tree_end_postponement', return_value=2025)
    def test_assert_get_context(self, mock_max_postponement):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertIsInstance(response.context['training_version_form'], UpdateTrainingVersionForm)
        self.assertEqual(response.context['training_obj'], self.training_obj)
        self.assertEqual(response.context['training_version_obj'], self.training_version_obj)
        self.assertEqual(response.context['group_obj'], self.group_obj)
        self.assertIn('is_finality_types', response.context)

        expected_tabs = [
            {
                "text": _("Identification"),
                "active": True,
                "display": True,
                "include_html": "tree_version/training/blocks/identification.html"
            },
            {
                "text": _("Diplomas /  Certificates"),
                "active": False,
                "display": True,
                "include_html": "tree_version/training/blocks/diplomas_certificates.html"
            },
        ]
        self.assertEqual(response.context['tabs'], expected_tabs)


class TestTrainingVersionUpdatePostView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.training_version_obj = SpecificProgramTreeVersionFactory()
        cls.group_obj = GroupFactory(
            entity_identity=GroupIdentity(
                code=cls.training_version_obj.tree.root_node.code,
                year=cls.training_version_obj.tree.root_node.year
            )
        )
        cls.training_obj = TrainingFactory()

        cls.url = reverse(
            'training_version_update',
            kwargs={"code": cls.group_obj.code, "year": cls.group_obj.year}
        )

        # Create db data for permission
        group_year_db = GroupYearDBFactory(partial_acronym=cls.group_obj.code, academic_year__year=cls.group_obj.year,)
        cls.central_manager = CentralManagerFactory(entity=group_year_db.management_entity)

    def setUp(self):
        self.client.force_login(self.central_manager.person.user)

        # Mock for service
        self.get_group_patcher = mock.patch(
            "program_management.views.tree_version.update_training.get_group_service.get_group",
            return_value=self.group_obj
        )
        self.mocked_get_group = self.get_group_patcher.start()
        self.addCleanup(self.get_group_patcher.stop)

        self.get_training_patcher = mock.patch(
            "program_management.views.tree_version.update_training.get_training_service.get_training",
            return_value=self.training_obj
        )
        self.mocked_get_training = self.get_training_patcher.start()
        self.addCleanup(self.get_training_patcher.stop)

        self.get_training_version_patcher = mock.patch(
            "program_management.views.tree_version.update_training."
            "get_program_tree_version_from_node_service.get_program_tree_version_from_node",
            return_value=self.training_version_obj
        )
        self.mocked_get_training_version = self.get_training_version_patcher.start()
        self.addCleanup(self.get_training_version_patcher.stop)

    def test_case_when_user_not_logged(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_when_user_has_no_permission(self):
        a_person_without_permission = PersonFactory()
        self.client.force_login(a_person_without_permission.user)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
