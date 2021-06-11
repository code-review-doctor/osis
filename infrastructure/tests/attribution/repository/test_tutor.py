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

from attribution.models.attribution_new import AttributionNew
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from ddd.logic.attribution.domain.model.tutor import Tutor
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder

from infrastructure.attribution.repository.tutor import TutorRepository
from infrastructure.learning_unit.repository.learning_unit import LearningUnitRepository


class TutorRepositoryTestCase(TestCase):

    def setUp(self):
        self.tutor_repository = TutorRepository()
        self.learning_rep = LearningUnitRepository()

    def test_should_return_empty_list_when_no_attribution_found(self):
        ue_without_attribution = LearningUnitYearFactory(
            academic_year__current=True
        )
        entity_id = LearningUnitIdentityBuilder.build_from_code_and_year(
            code=ue_without_attribution.acronym,
            year=ue_without_attribution.academic_year.year
        )
        results = self.tutor_repository.search(learning_unit_identity=entity_id)
        self.assertEqual(len(results), 0)

    def test_should_return_2_attributions(self):
        ue_with_attributions = LearningUnitYearFactory(
            academic_year__current=True
        )
        attribution_1 = AttributionChargeNewFactory(
            learning_component_year__learning_unit_year=ue_with_attributions,
            attribution__tutor__person__last_name='Dupont'
        )
        attribution_2 = AttributionChargeNewFactory(
            learning_component_year__learning_unit_year=ue_with_attributions,
            attribution__tutor__person__last_name='Bastin'
        )

        entity_id = LearningUnitIdentityBuilder.build_from_code_and_year(
            code=ue_with_attributions.acronym,
            year=ue_with_attributions.academic_year.year
        )
        results = self.tutor_repository.search(learning_unit_identity=entity_id)
        self.assertEqual(len(results), 2)
        self._assert_should_correctly_map_database_fields_with_dto_fields(
            results[0],
            attribution_2.attribution,
            ue_with_attributions
        )
        self._assert_should_correctly_map_database_fields_with_dto_fields(
            results[1],
            attribution_1.attribution,
            ue_with_attributions
        )

    def _assert_should_correctly_map_database_fields_with_dto_fields(
            self,
            ddd_tutor_attribution: Tutor,
            db_attribution: AttributionNew,
            ue: LearningUnitYear
    ):
        self.assertEqual(
            ddd_tutor_attribution.last_name,
            db_attribution.tutor.person.last_name
        )
        self.assertEqual(
            ddd_tutor_attribution.first_name,
            db_attribution.tutor.person.first_name
        )
        self.assertEqual(len(ddd_tutor_attribution.attributions), 1)
        a_ddd_attribution = ddd_tutor_attribution.attributions[0]
        self.assertEqual(a_ddd_attribution.function, db_attribution.function)
        self.assertEqual(a_ddd_attribution.entity_id.uuid, db_attribution.id)
        self.assertEqual(a_ddd_attribution.learning_unit.code, ue.acronym)
        self.assertEqual(a_ddd_attribution.learning_unit.year, ue.academic_year.year)
