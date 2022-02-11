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
from django.test import TestCase, RequestFactory
from django.urls import reverse

from reference.api.serializers.high_school import HighSchoolDetailSerializer, HighSchoolListSerializer
from reference.tests.factories.high_school import HighSchoolFactory


class HighSchoolListSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.high_school = HighSchoolFactory()
        cls.high_school.name = cls.high_school.organization.name
        cls.high_school.acronym = cls.high_school.organization.acronym
        url = reverse('reference_api_v1:high_school-list')
        cls.serializer = HighSchoolListSerializer(cls.high_school, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'url',
            'uuid',
            'name',
            'acronym',
            'type',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class HighSchoolDetailSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.high_school = HighSchoolFactory()
        cls.high_school.name = cls.high_school.organization.name
        cls.high_school.acronym = cls.high_school.organization.acronym
        url = reverse('reference_api_v1:high_school-detail', kwargs={'uuid': cls.high_school.uuid})
        cls.serializer = HighSchoolDetailSerializer(cls.high_school, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'url',
            'uuid',
            'name',
            'acronym',
            'type',
            'phone',
            'fax',
            'email',
            'start_year',
            'end_year',
            'linguistic_regime',
            'country',
            'zipcode',
            'city',
            'street',
            'street_number',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)
