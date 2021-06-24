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

from django.test import TestCase

from attribution.models.attribution_class import AttributionClass
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from attribution.tests.factories.attribution_class import AttributionClassFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from ddd.logic.attribution.builder.tutor_identity_builder import TutorIdentityBuilder
from ddd.logic.attribution.tests.factory.tutor import TutorWithDistributedEffectiveClassesFactory, \
    Tutor9999IdentityFactory
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.tests.factory.effective_class import LDROI1001XEffectiveClassIdentityFactory
from infrastructure.attribution.repository.tutor import TutorRepository
from infrastructure.learning_unit.repository.learning_unit import LearningUnitRepository
from learning_unit.tests.factories.learning_class_year import LearningClassYearFactory


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

    def test_should_filter_on_effective_class(self):
        class_identity = LDROI1001XEffectiveClassIdentityFactory()
        AttributionClassFactory(
            learning_class_year__acronym=class_identity.class_code,
            learning_class_year__learning_component_year__learning_unit_year__acronym=class_identity.learning_unit_identity.code,
            learning_class_year__learning_component_year__learning_unit_year__academic_year__year=class_identity.learning_unit_identity.year,
        )
        for _ in range(5):
            AttributionClassFactory()
        result = self.tutor_repository.search(effective_class_identity=class_identity)
        self.assertTrue(len(result) == 1)

    def test_should_filter_on_list_of_tutor_identities(self):
        tutor_identity = Tutor9999IdentityFactory()
        AttributionClassFactory(
            attribution_charge__attribution__tutor__person__global_id=tutor_identity.personal_id_number,
        )
        for _ in range(5):
            AttributionClassFactory()
        result = self.tutor_repository.search(entity_ids=[tutor_identity])
        self.assertTrue(len(result) == 1)

    def test_should_correctly_map_tutor_aggregate_to_database_fields(self):
        tutor_to_persist = TutorWithDistributedEffectiveClassesFactory()
        first_distributed_class = tutor_to_persist.distributed_effective_classes[0]
        learning_unit_id = first_distributed_class.effective_class.learning_unit_identity
        person = PersonFactory(global_id=tutor_to_persist.entity_id.personal_id_number)
        ue = LearningUnitYearFactory(
            academic_year__year=learning_unit_id.year,
            acronym=learning_unit_id.code
        )
        distributed_effective_classes = first_distributed_class
        learning_class_year = LearningClassYearFactory(
            learning_component_year__learning_unit_year=ue,
            acronym=distributed_effective_classes.effective_class.class_code
        )
        AttributionChargeNewFactory(
            learning_component_year=learning_class_year.learning_component_year,
            attribution__uuid=first_distributed_class.attribution.uuid,
            attribution__tutor__person=person
        )

        self.tutor_repository.save(tutor_to_persist)
        attribution_classes_db = AttributionClass.objects.all()
        self.assertEqual(attribution_classes_db.count(), 1)
        self.assertEqual(
            attribution_classes_db.first().allocation_charge,
            distributed_effective_classes.distributed_volume
        )

    def test_should_correctly_map_database_fields_to_tutor_aggregate(self):
        person = PersonFactory(global_id="123456")
        ue = LearningUnitYearFactory()
        learning_class_year = LearningClassYearFactory(learning_component_year__learning_unit_year=ue)
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year=learning_class_year.learning_component_year,
            attribution__tutor__person=person,
        )
        attribution_class = AttributionClassFactory(
            learning_class_year=learning_class_year,
            attribution_charge=attribution_charge,
            allocation_charge=Decimal(5.0),
        )
        tutor = self.tutor_repository.get(
            entity_id=TutorIdentityBuilder.build_from_personal_id_number(personal_id_number=person.global_id)
        )

        self.assertEqual(tutor.entity_id.personal_id_number, person.global_id)

        learning_unit_id = tutor.distributed_effective_classes[0].effective_class.learning_unit_identity
        self.assertEqual(learning_unit_id.code, ue.acronym)
        self.assertEqual(learning_unit_id.year, ue.academic_year.year)

        distributed_effective_class = tutor.distributed_effective_classes[0]
        self.assertEqual(distributed_effective_class.effective_class.class_code, learning_class_year.acronym)
        self.assertEqual(distributed_effective_class.effective_class.learning_unit_identity.code, ue.acronym)
        self.assertEqual(distributed_effective_class.effective_class.learning_unit_identity.year, ue.academic_year.year)
        self.assertEqual(distributed_effective_class.distributed_volume, attribution_class.allocation_charge)

    def test_should_correctly_unassign_class_from_tutor(self):
        person = PersonFactory(global_id="123456")
        ue = LearningUnitYearFactory()
        learning_class_year = LearningClassYearFactory(learning_component_year__learning_unit_year=ue)
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year=learning_class_year.learning_component_year,
            attribution__tutor__person=person,
        )
        distrubuted_class_db = AttributionClassFactory(
            learning_class_year=learning_class_year,
            attribution_charge=attribution_charge,
            allocation_charge=Decimal(5.0),
        )
        tutor = self.tutor_repository.get(
            entity_id=TutorIdentityBuilder.build_from_personal_id_number(personal_id_number=person.global_id)
        )

        self.assertTrue(AttributionClass.objects.filter(pk=distrubuted_class_db.pk).exists())
        tutor.distributed_effective_classes = []
        self.tutor_repository.save(tutor)
        self.assertFalse(AttributionClass.objects.filter(pk=distrubuted_class_db.pk).exists())
