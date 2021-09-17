##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from types import SimpleNamespace

from django.conf import settings
from django.test import TestCase

from base.models.enums.learning_component_year_type import LECTURING
from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from learning_unit.api.serializers.effective_class import EffectiveClassSerializer


class EffectiveClassSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        ns = SimpleNamespace(
            code="Z",
            title_fr="TITRE",
            title_en="TITLE",
            teaching_place_uuid="1234664341",
            derogation_quadrimester=DerogationQuadrimester.Q1.name,
            session_derogation=DerogationSession.DEROGATION_SESSION_1XX.name,
            volume_q1=0.0,
            volume_q2=10.0,
            type=LECTURING,
            campus_name="Campus",
            organization_name="UCLouvain"
        )

        cls.serializer = EffectiveClassSerializer(ns, context={'language': settings.LANGUAGE_CODE_EN})

    def test_contains_expected_fields(self):
        expected_fields = [
            'code',
            'title_fr',
            'title_en',
            'teaching_place_uuid',
            'derogation_quadrimester',
            'derogation_quadrimester_text',
            'session_derogation',
            'volume_q1',
            'volume_q2',
            'type',
            'campus_name',
            'organization_name',
        ]
        self.assertCountEqual(list(self.serializer.data.keys()), expected_fields)
