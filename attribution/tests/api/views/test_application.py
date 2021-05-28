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
import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from attribution.api.views.application import ApplicationListCreateView, ApplicationUpdateDeleteView, \
    RenewAttributionsAboutToExpire
from base.tests.factories.tutor import TutorFactory
from ddd.logic.application.commands import ApplyOnVacantCourseCommand, SearchApplicationByApplicantCommand, \
    DeleteApplicationCommand, UpdateApplicationCommand, GetAttributionsAboutToExpireCommand, \
    RenewMultipleAttributionsCommand


class ApplicationCreateListViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory(person__global_id="2656859898")
        cls.url = reverse('attribution_api_v1:' + ApplicationListCreateView.name)

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
        methods_not_allowed = ['delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_assert_call_message_bus_invoke_apply_on_vacant_course_command(self):
        post_data = {
            "code": "LDROI1200",
            "lecturing_volume": "20.0",
            "practical_volume": "25.0",
            "course_summary": "Résumé d'un cours LDROI1200",
            "remark": "Remarque"
        }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(self.message_bus_mocked.called)
        invoke_args = self.message_bus_mocked.call_args[0]

        self.assertIsInstance(invoke_args[0], ApplyOnVacantCourseCommand)

    def test_get_assert_call_message_bus_invoke_search_application_by_applicant_command(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(self.message_bus_mocked.called)
        invoke_args = self.message_bus_mocked.call_args[0]

        self.assertIsInstance(invoke_args[0], SearchApplicationByApplicantCommand)


class ApplicationUpdateDeleteViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory(person__global_id="2656859898")
        cls.url = reverse(
            'attribution_api_v1:' + ApplicationUpdateDeleteView.name,
            kwargs={'application_uuid': uuid.uuid4()}
        )

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
        methods_not_allowed = ['get', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_assert_call_message_bus_invoke_delete_application_command(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(self.message_bus_mocked.called)
        invoke_args = self.message_bus_mocked.call_args[0]

        self.assertIsInstance(invoke_args[0], DeleteApplicationCommand)

    def test_put_assert_call_message_bus_invoke_update_application_command(self):
        put_data = {
            "lecturing_volume": "20.0",
            "practical_volume": "27.0",
            "course_summary": "Mise à jour du résumé du cours LDROI1200",
            "remark": "Remarque mise à jour"
        }

        response = self.client.put(self.url, data=put_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(self.message_bus_mocked.called)
        invoke_args = self.message_bus_mocked.call_args[0]

        self.assertIsInstance(invoke_args[0], UpdateApplicationCommand)


class RenewAttributionsAboutToExpireTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tutor = TutorFactory(person__global_id="2656859898")
        cls.url = reverse('attribution_api_v1:' + RenewAttributionsAboutToExpire.name)

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
        methods_not_allowed = ['patch', 'delete']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_assert_call_message_bus_invoke_get_attributions_about_to_expire_command(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(self.message_bus_mocked.called)
        invoke_args = self.message_bus_mocked.call_args[0]

        self.assertIsInstance(invoke_args[0], GetAttributionsAboutToExpireCommand)

    def test_post_codes_should_not_be_empty(self):
        post_data = {
            'codes': []
        }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_assert_call_message_bus_invoke_renew_multiple_attributions_command(self):
        post_data = {
            'codes': ['LDROI1200', 'LAGRO4567']
        }

        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(self.message_bus_mocked.called)
        invoke_args = self.message_bus_mocked.call_args[0]

        self.assertIsInstance(invoke_args[0], RenewMultipleAttributionsCommand)
