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
from django.test import TestCase

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from ddd.logic.learning_unit.tests.factory.learning_unit import LDROI1001LearningUnitIdentityFactory
from infrastructure.attribution.domain.service.tutor_attribution import TutorAttributionToLearningUnitTranslator


class TestTutorAttributionToLearningUnitTranslator(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.translator = TutorAttributionToLearningUnitTranslator()

    def test_should_order_by_last_name_and_first_name(self):
        identity = LDROI1001LearningUnitIdentityFactory()
        for _ in range(3):
            AttributionChargeNewFactory(
                learning_component_year__learning_unit_year__acronym=identity.code,
                learning_component_year__learning_unit_year__academic_year__year=identity.year,
                allocation_charge=10.0,
            )
        result = self.translator.search_attributions_to_learning_unit(identity)
        ordered_by_last_name_first_name = list(sorted(result, key=lambda elem: (elem.last_name, elem.first_name)))
        self.assertListEqual(result, ordered_by_last_name_first_name)

    def test_should_filter_by_learning_unit(self):
        identity = LDROI1001LearningUnitIdentityFactory()
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year__learning_unit_year__acronym=identity.code,
            learning_component_year__learning_unit_year__academic_year__year=identity.year,
            allocation_charge=10.0,
        )
        for _ in range(3):
            AttributionChargeNewFactory()  # Build other attributions
        result = self.translator.search_attributions_to_learning_unit(identity)
        self.assertTrue(len(result) == 1)
        self.assertEqual(result[0].attribution_uuid, attribution_charge.attribution.uuid)
