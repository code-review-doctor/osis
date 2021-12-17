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
import uuid

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.user import UserFactory
from organisation.api.serializers.entities import EntitySerializer
from organisation.api.views.entities import EntitiesListView


class EntitesListViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entity_version = EntityVersionFactory(entity__organization__acronym='UCL')
        cls.url = reverse('organisation_api_v1:' + EntitiesListView.name, kwargs={
            'organisation_code': cls.entity_version.entity.organization.acronym
        })
        cls.user = UserFactory()

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_results_assert_key(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()['results']
        self.assertEqual(len(results), 1)

        self.assertCountEqual(
            list(results[0].keys()), [
                'uuid',
                'organization_name',
                'organization_acronym',
                'title',
                'acronym',
                'entity_type',
                'entity_type_text',
                'start_date',
                'end_date',
                'logo',
            ])


class EntiteDetailTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entity_version = EntityVersionFactory(entity__organization__acronym='UCL')

        cls.user = UserFactory()
        cls.url = reverse('organisation_api_v1:entity-detail', kwargs={
            'organisation_code': cls.entity_version.entity.organization.acronym,
            'uuid': cls.entity_version.uuid
        })

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

    def test_get_valid_entity(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = EntitySerializer(
            self.entity_version,
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_entity_case_not_found(self):
        invalid_url = reverse('organisation_api_v1:entity-detail', kwargs={
            'organisation_code': self.entity_version.entity.organization.acronym,
            'uuid': uuid.uuid4()
        })
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
