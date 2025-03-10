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

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.tests.factories.entity_version_address import EntityVersionAddressFactory
from base.tests.factories.user import UserFactory
from organisation.api.views.addresses import AddressesListView


class AddressesListViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.address = EntityVersionAddressFactory(
            entity_version__entity__organization__acronym='UCL'
        )
        cls.url = reverse('organisation_api_v1:' + AddressesListView.name, kwargs={
            'organisation_code': cls.address.entity_version.entity.organization.acronym,
            'uuid': cls.address.entity_version.uuid
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

        self.assertCountEqual(
            list(response.data.keys()), [
                'city',
                'location',
                'street',
                'street_number',
                'postal_code',
                'state',
                'country_iso_code',
                'is_main',
            ])
