##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest import mock

from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse

from base.models.enums.education_group_types import TrainingType
from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.user import UserFactory
from base.utils.urls import reverse_with_get
from education_group.ddd.domain.group import Group
from education_group.models.enums.cohort_name import CohortName
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory
from program_management.tests.factories.element import ElementGroupYearFactory


class TestTrainingReadAdministrativeData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonWithPermissionsFactory('view_educationgroup')
        cls.training_version = EducationGroupVersionFactory(
            offer__acronym="DROI2M",
            offer__partial_acronym="LDROI200M",
            offer__academic_year__year=2019,
            offer__education_group_type__name=TrainingType.PGRM_MASTER_120.name,
            root_group__acronym="DROI2M",
            root_group__partial_acronym="LDROI200M",
            root_group__academic_year__year=2019,
            root_group__education_group_type__name=TrainingType.PGRM_MASTER_120.name,
        )
        ElementGroupYearFactory(group_year=cls.training_version.root_group)
        cls.url = reverse('training_administrative_data', kwargs={'year': 2019, 'code': 'LDROI200M'})

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

        self.perm_patcher = mock.patch(
            "education_group.views.training.administrative_data_read.TrainingReadAdministrativeData."
            "have_administrative_data_tab",
            return_value=True
        )
        self.mocked_perm = self.perm_patcher.start()
        self.addCleanup(self.perm_patcher.stop)

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_case_user_have_not_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_case_training_unauthorized_administrative_data_tab(self):
        with mock.patch(
            "education_group.views.training.administrative_data_read.TrainingReadAdministrativeData."
            "have_administrative_data_tab",
            return_value=False
        ):
            response = self.client.get(self.url)
            expected_redirect = reverse('training_identification', kwargs={'year': 2019, 'code': 'LDROI200M'})
            self.assertRedirects(response, expected_redirect)

    def test_case_training_not_exists(self):
        dummy_url = reverse('training_administrative_data', kwargs={'year': 2018, 'code': 'DUMMY100B'})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "education_group_app/training/administrative_data.html")

    def test_assert_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context['person'], self.person)
        self.assertEqual(response.context['group_year'], self.training_version.root_group)
        self.assertEqual(response.context['education_group_version'], self.training_version)
        expected_tree_json_url = reverse_with_get(
            'tree_json',
            kwargs={'root_id': self.training_version.root_group.element.pk},
            get={"path": str(self.training_version.root_group.element.pk)}
        )
        self.assertEqual(response.context['tree_json_url'], expected_tree_json_url)
        self.assertIsInstance(response.context['group'], Group)
        self.assertIn("learning_unit_enrollment_dates", response.context)
        self.assertIn("administrative_dates", response.context)
        self.assertIn("additional_informations", response.context)
        self.assertIn("mandataries", response.context)
        self.assertIn("program_managers", response.context)

    def test_assert_active_tabs_is_administrative_data_and_others_are_not_active(self):
        from education_group.views.training.common_read import Tab

        response = self.client.get(self.url)

        self.assertTrue(response.context['tab_urls'][Tab.ADMINISTRATIVE_DATA]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.ACCESS_REQUIREMENTS]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.IDENTIFICATION]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.DIPLOMAS_CERTIFICATES]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.CONTENT]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.UTILIZATION]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.SKILLS_ACHIEVEMENTS]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.GENERAL_INFO]['active'])

    def test_assert_program_manager_only_without_cohorte_displayed(self):
        ProgramManagerFactory(education_group=self.training_version.offer.education_group)
        ProgramManagerFactory(
            education_group=self.training_version.offer.education_group,
            cohort=CohortName.FIRST_YEAR.name,
        )

        response = self.client.get(self.url)
        self.assertEqual(len(response.context["program_managers"]), 1)
