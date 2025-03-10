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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.models.academic_calendar import AcademicCalendar
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.user import UserFactory
from reference.api.serializers.academic_calendar import AcademicCalendarSerializer
from reference.api.views.academic_calendar import AcademicCalendarList


class AcademicCalendarListTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('reference_api_v1:' + AcademicCalendarList.name)

        AcademicCalendarFactory()
        AcademicCalendarFactory()

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_ensure_response_have_next_previous_results_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)

        self.assertTrue('count' in response.data)
        expected_count = AcademicCalendar.objects.all().count()
        self.assertEqual(response.data['count'], expected_count)

    def test_get_ensure_default_order(self):
        """ This test ensure that default order is data_year [ASC Order]"""

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        academic_calendar_qs = AcademicCalendar.objects.order_by('data_year')
        serializer = AcademicCalendarSerializer(academic_calendar_qs, many=True)
        self.assertEqual(response.data['results'], serializer.data)
