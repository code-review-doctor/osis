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
from django.urls import reverse
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APITestCase
from django.utils.translation import gettext_lazy as _

from attribution.api.views.vacant_course import VacantCourseListView
from base.tests.factories.tutor import TutorFactory
from ddd.logic.application.commands import SearchVacantCoursesCommand


class VacantCourseListViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory(person__global_id="2656859898")
        cls.url = reverse('attribution_api_v1:' + VacantCourseListView.name)

    def setUp(self):
        self.client.force_authenticate(user=self.tutor.person.user)

        self.patch_message_bus = mock.patch(
            "attribution.api.views.application.message_bus_instance.invoke",
            return_value=None
        )
        self.message_bus_mocked = self.patch_message_bus.start()
        self.addCleanup(self.patch_message_bus.stop)

    def test_user_not_logged_assert_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assert_methods_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch', 'post']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_assert_one_filter_criteria_should_be_filled(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                api_settings.NON_FIELD_ERRORS_KEY: [
                    _('Please precise at least a faculty or a code (or a part of a code)')
                ]
            }
        )

    def test_get_assert_call_message_bus_invoke_search_vacant_courses_command(self):
        response = self.client.get(self.url, data={'code': 'LDROI'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(self.message_bus_mocked.called)
        invoke_args = self.message_bus_mocked.call_args[0]

        self.assertIsInstance(invoke_args[0], SearchVacantCoursesCommand)
