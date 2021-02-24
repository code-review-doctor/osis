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
from decimal import Decimal
from types import SimpleNamespace

from django.test import TestCase

from attribution.api.serializers.attribution import AttributionSerializer
from attribution.models.enums.function import Functions


class AttributionSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        attribution_obj = SimpleNamespace(
            acronym="LDROI1001",
            title="Introduction aux droits Partie I",
            year=2020,
            credits=Decimal("15.5"),
            start_year=2015,
            function=Functions.COORDINATOR.name,
        )
        cls.serializer = AttributionSerializer(attribution_obj)

    def test_contains_expected_fields(self):
        expected_fields = [
            'acronym',
            'title',
            'year',
            'credits',
            'start_year',
            'function',
            'function_text',
            'catalog_app_url',
            'schedule_app_url',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_function_text_correctly_computed(self):
        self.assertEquals(self.serializer.data['function_text'], Functions.COORDINATOR.value)

    def test_ensure_catalog_app_url_correctly_computed(self):
        self.assertEquals(self.serializer.data['catalog_app_url'], "")

    def test_ensure_schedule_app_url_correctly_computed(self):
        self.assertEquals(self.serializer.data['schedule_app_url'], "")
