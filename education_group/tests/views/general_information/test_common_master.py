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

from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from base.tests.factories.admission_condition import AdmissionConditionFactory
from base.tests.factories.education_group_year import EducationGroupYearCommonMasterFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.factories.user import UserFactory
from education_group.views.general_information.common_master import Tab


class TestCommonMasterAdmissionCondition(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonWithPermissionsFactory('view_educationgroup')
        cls.common_master_education_group_year = EducationGroupYearCommonMasterFactory(academic_year__year=2018)
        AdmissionConditionFactory(education_group_year=cls.common_master_education_group_year)
        cls.url = reverse('common_master_access_requirements', kwargs={'year': 2018})

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_case_user_have_not_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_case_common_and_admission_condition_not_exists(self):
        dummy_url = reverse('common_master_access_requirements', kwargs={'year': 1990})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_case_common_exist_but_admission_condition_not_exist(self):
        obj = EducationGroupYearCommonMasterFactory(academic_year__year=1990)

        dummy_url = reverse('common_master_access_requirements', kwargs={'year': 1990})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['object'], obj)
        self.assertEqual(response.context['access_requirements'].education_group_year, obj)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "education_group_app/general_information/common_master.html")

    def test_assert_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context['object'], self.common_master_education_group_year)
        expected_publish_url = reverse('publish_common_master_access_requirements', kwargs={
            'year': self.common_master_education_group_year.academic_year.year
        })
        self.assertEqual(response.context['publish_url'], expected_publish_url)
        self.assertEqual(
            response.context['access_requirements'],
            self.common_master_education_group_year.admissioncondition
        )
        self.assertIn("tab_urls", response.context)
        self.assertIn("can_edit_information", response.context)

    def test_assert_active_tabs_is_content_and_others_are_not_active(self):
        response = self.client.get(self.url)

        self.assertEqual(len(response.context['tab_urls']), 1)
        self.assertTrue(response.context['tab_urls'][Tab.ACCESS_REQUIREMENTS]['active'])
