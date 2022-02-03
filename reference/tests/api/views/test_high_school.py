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
import uuid

from django.db.models import F
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APITestCase

from base.tests.factories.user import UserFactory
from reference.api.serializers.high_school import HighSchoolDetailSerializer, HighSchoolListSerializer
from reference.models.high_school import HighSchool
from reference.tests.factories.high_school import HighSchoolFactory


class GetAllHighSchoolTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('reference_api_v1:high_school-list')

        HighSchoolFactory()
        HighSchoolFactory()
        HighSchoolFactory()

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

    def test_get_all_high_school_ensure_response_have_next_previous_results_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)

        self.assertTrue('count' in response.data)
        expected_count = HighSchool.objects.all().count()
        self.assertEqual(response.data['count'], expected_count)

    def test_get_all_high_school_ensure_default_order(self):
        """ This test ensure that default order is organization name [ASC Order]"""

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        high_schools = HighSchool.objects.all().order_by('organization__name').annotate(
            acronym=F('organization__acronym'),
            name=F('organization__name'),
        )
        serializer = HighSchoolListSerializer(
            high_schools,
            many=True,
            context={'request': RequestFactory().get(self.url)}
        )
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_all_high_school_specify_ordering_field(self):
        ordering_managed = [('organization__name', 'name'), ('organization__acronym', 'acronym')]

        for db_order, api_order in ordering_managed:
            query_string = {api_settings.ORDERING_PARAM: api_order}
            response = self.client.get(self.url, kwargs=query_string)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            high_schools = HighSchool.objects.all().order_by(db_order).annotate(
                acronym=F('organization__acronym'),
                name=F('organization__name'),
            )
            serializer = HighSchoolListSerializer(
                high_schools,
                many=True,
                context={'request': RequestFactory().get(self.url, query_string)},
            )
            self.assertEqual(response.data['results'], serializer.data)


class GetHighSchoolTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.high_school = HighSchoolFactory()
        cls.high_school.name = cls.high_school.organization.name
        cls.high_school.acronym = cls.high_school.organization.acronym

        cls.user = UserFactory()
        cls.url = reverse('reference_api_v1:high_school-detail', kwargs={'uuid': cls.high_school.uuid})

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

    def test_get_valid_high_school(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = HighSchoolDetailSerializer(
            self.high_school,
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_high_school_case_not_found(self):
        invalid_url = reverse('reference_api_v1:high_school-detail', kwargs={'uuid': uuid.uuid4()})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
