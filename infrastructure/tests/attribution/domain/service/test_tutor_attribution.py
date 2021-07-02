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
from ddd.logic.attribution.tests.factory.tutor import Tutor9999IdentityFactory
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
            )
        result = self.translator.search_attributions_to_learning_unit(identity)
        ordered_by_last_name_first_name = list(sorted(result, key=lambda elem: (elem.last_name, elem.first_name)))
        self.assertListEqual(result, ordered_by_last_name_first_name)

    def test_should_filter_by_learning_unit(self):
        identity = LDROI1001LearningUnitIdentityFactory()
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year__learning_unit_year__acronym=identity.code,
            learning_component_year__learning_unit_year__academic_year__year=identity.year,
        )
        for _ in range(3):
            AttributionChargeNewFactory()  # Build other attributions
        result = self.translator.search_attributions_to_learning_unit(identity)
        self.assertTrue(len(result) == 1)
        self.assertEqual(result[0].attribution_uuid, attribution_charge.attribution.uuid)

    def test_should_get_by_tutor_and_learning_unit(self):
        tutor_identity = Tutor9999IdentityFactory()
        learn_unit_identity = LDROI1001LearningUnitIdentityFactory()
        attribution_charge = AttributionChargeNewFactory(
            attribution__tutor__person__global_id=tutor_identity.personal_id_number,
            learning_component_year__learning_unit_year__acronym=learn_unit_identity.code,
            learning_component_year__learning_unit_year__academic_year__year=learn_unit_identity.year,
        )
        for _ in range(3):
            AttributionChargeNewFactory()  # Build other attributions
        result = self.translator.get_tutor_attribution_to_learning_unit(tutor_identity, learn_unit_identity)
        self.assertEqual(result.personal_id_number, attribution_charge.attribution.tutor.person.global_id)
        self.assertEqual(result.attributed_volume_to_learning_unit, attribution_charge.allocation_charge)

    def test_should_correctly_map_database_fields_to_dto(self):
        tutor_identity = Tutor9999IdentityFactory()
        learn_unit_identity = LDROI1001LearningUnitIdentityFactory()
        attribution_charge = AttributionChargeNewFactory(
            attribution__tutor__person__global_id=tutor_identity.personal_id_number,
            learning_component_year__learning_unit_year__acronym=learn_unit_identity.code,
            learning_component_year__learning_unit_year__academic_year__year=learn_unit_identity.year,
        )
        result = self.translator.get_tutor_attribution_to_learning_unit(tutor_identity, learn_unit_identity)
        self.assertEqual(result.attribution_uuid, attribution_charge.attribution.uuid)
        person_database = attribution_charge.attribution.tutor.person
        self.assertEqual(result.learning_unit_code, learn_unit_identity.code)
        self.assertEqual(result.learning_unit_year, learn_unit_identity.year)
        self.assertEqual(result.attribution_uuid, attribution_charge.attribution.uuid)
        self.assertEqual(result.last_name, person_database.last_name)
        self.assertEqual(result.first_name, person_database.first_name)
        self.assertEqual(result.personal_id_number, person_database.global_id)
        self.assertEqual(result.function, attribution_charge.attribution.function)
        self.assertEqual(result.attributed_volume_to_learning_unit, attribution_charge.allocation_charge)
        self.assertEqual(result.classes, [])
