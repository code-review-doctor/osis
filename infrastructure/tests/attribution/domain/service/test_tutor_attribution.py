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

from django.test import TestCase

from attribution.models.attribution_new import AttributionNew
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.models.enums import learning_component_year_type
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from ddd.logic.learning_unit.tests.factory.learning_unit import LDROI1001LearningUnitIdentityFactory, \
    LDROI1002ExternalLearningUnitFactory
from infrastructure.effective_class_repartition.domain.service.tutor_attribution import \
    TutorAttributionToLearningUnitTranslator


class TestSearchTutorAttributionToLearningUnitTranslator(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.translator = TutorAttributionToLearningUnitTranslator()
        cls.function_to_test = cls.translator.search_attributions_to_learning_unit
        cls.identity = LDROI1001LearningUnitIdentityFactory()
        cls.learning_unit_year = LearningUnitYearFactory(
            acronym=cls.identity.code,
            academic_year__year=cls.identity.year,
        )

    def test_should_order_by_last_name_and_first_name(self):
        for _ in range(3):
            AttributionChargeNewFactory(
                learning_component_year__learning_unit_year=self.learning_unit_year,
            )
        result = self.function_to_test(self.identity)
        ordered_by_last_name_first_name = list(sorted(result, key=lambda elem: (elem.last_name, elem.first_name)))
        self.assertListEqual(result, ordered_by_last_name_first_name)

    def test_should_filter_by_learning_unit(self):
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year__learning_unit_year=self.learning_unit_year,
        )
        for _ in range(3):
            AttributionChargeNewFactory()  # Build other attributions
        result = self.function_to_test(self.identity)
        self.assertTrue(len(result) == 1)
        self.assertEqual(result[0].attribution_uuid, attribution_charge.attribution.uuid)

    def test_should_renvoyer_aucun_resultat(self):
        inexisting = LDROI1002ExternalLearningUnitFactory()
        result = self.function_to_test(inexisting)
        self.assertListEqual(list(), result)

    def test_should_renvoyer_code_annee_unite_enseignement(self):
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year__learning_unit_year=self.learning_unit_year,
        )
        result = self.function_to_test(self.identity)[0]
        self.assertEqual(result.learning_unit_code, attribution_charge.attribution.learning_container_year.acronym)
        self.assertEqual(
            result.learning_unit_year,
            attribution_charge.attribution.learning_container_year.academic_year.year
        )

    def test_should_renvoyer_detail_attribution(self):
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year__learning_unit_year=self.learning_unit_year,
        )
        result = self.function_to_test(self.identity)[0]
        self.assertEqual(result.attribution_uuid, attribution_charge.attribution.uuid)
        self.assertEqual(result.last_name, attribution_charge.attribution.tutor.person.last_name)
        self.assertEqual(result.first_name, attribution_charge.attribution.tutor.person.first_name)
        self.assertEqual(result.personal_id_number, attribution_charge.attribution.tutor.person.global_id)
        self.assertEqual(result.function, attribution_charge.attribution.function)

    def test_should_renvoyer_volume_partie_pratique(self):
        AttributionChargeNewFactory(
            learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES,
            learning_component_year__learning_unit_year=self.learning_unit_year,
            allocation_charge=10.0,
        )
        result = self.function_to_test(self.identity)[0]
        self.assertIsNone(result.lecturing_volume_attributed)
        self.assertEqual(result.practical_volume_attributed, 10.0)

    def test_should_renvoyer_volume_partie_magistrale(self):
        AttributionChargeNewFactory(
            learning_component_year__type=learning_component_year_type.LECTURING,
            learning_component_year__learning_unit_year=self.learning_unit_year,
            allocation_charge=20.0,
        )
        result = self.function_to_test(self.identity)[0]
        self.assertIsNone(result.practical_volume_attributed)
        self.assertEqual(result.lecturing_volume_attributed, 20.0)


class TestGetLearningUnitAttributionsTranslator(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.translator = TutorAttributionToLearningUnitTranslator()
        cls.function_to_test = cls.translator.get_learning_unit_attribution
        cls.identity = LDROI1001LearningUnitIdentityFactory()
        cls.learning_unit_year = LearningUnitYearFactory(
            acronym=cls.identity.code,
            academic_year__year=cls.identity.year,
        )

    def test_should_renvoyer_aucun_resultat(self):
        uuid_inexistant = uuid.uuid4()
        result = self.function_to_test(uuid_inexistant)
        self.assertIsNone(result)

    def test_should_renvoyer_code_annee_unite_enseignement(self):
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year__learning_unit_year=self.learning_unit_year,
        )
        result = self.function_to_test(attribution_charge.attribution.uuid)
        self.assertEqual(result.learning_unit_code, attribution_charge.attribution.learning_container_year.acronym)
        self.assertEqual(
            result.learning_unit_year,
            attribution_charge.attribution.learning_container_year.academic_year.year
        )

    def test_should_renvoyer_detail_attribution(self):
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year__learning_unit_year=self.learning_unit_year,
        )
        result = self.function_to_test(attribution_charge.attribution.uuid)
        self.assertEqual(result.attribution_uuid, attribution_charge.attribution.uuid)
        self.assertEqual(result.last_name, attribution_charge.attribution.tutor.person.last_name)
        self.assertEqual(result.first_name, attribution_charge.attribution.tutor.person.first_name)
        self.assertEqual(result.personal_id_number, attribution_charge.attribution.tutor.person.global_id)
        self.assertEqual(result.function, attribution_charge.attribution.function)

    def test_should_renvoyer_volume_partie_pratique(self):
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES,
            learning_component_year__learning_unit_year=self.learning_unit_year,
            allocation_charge=10.0,
        )
        result = self.function_to_test(attribution_charge.attribution.uuid)
        self.assertIsNone(result.lecturing_volume_attributed)
        self.assertEqual(result.practical_volume_attributed, 10.0)

    def test_should_renvoyer_volume_partie_magistrale(self):
        attribution_charge = AttributionChargeNewFactory(
            learning_component_year__type=learning_component_year_type.LECTURING,
            learning_component_year__learning_unit_year=self.learning_unit_year,
            allocation_charge=20.0,
        )
        result = self.function_to_test(attribution_charge.attribution.uuid)
        self.assertIsNone(result.practical_volume_attributed)
        self.assertEqual(result.lecturing_volume_attributed, 20.0)


class TestGetByEnseignantTranslator(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.translator = TutorAttributionToLearningUnitTranslator()
        cls.function_to_test = cls.translator.get_by_enseignant
        cls.identity = LDROI1001LearningUnitIdentityFactory()
        cls.annee = cls.identity.academic_year.year
        cls.learning_unit_year = LearningUnitYearFactory(
            acronym=cls.identity.code,
            academic_year__year=cls.identity.year,
        )
        cls.matricule_fgs_enseignant = '12345678'

    def test_should_renvoyer_aucun_resultat(self):
        uuid_inexistant = uuid.uuid4()
        result = self.function_to_test(uuid_inexistant, self.annee)
        self.assertListEqual(list(), result)

    def test_should_trouver_3_attributions(self):
        for _ in range(3):
            AttributionChargeNewFactory(
                attribution__tutor__person__global_id=self.matricule_fgs_enseignant,
                learning_component_year__learning_unit_year__academic_year__year=self.annee,
            )
        result = self.function_to_test(self.matricule_fgs_enseignant, self.annee)
        self.assertEqual(len(result), 3)

    def test_should_renvoyer_code_annee_unite_enseignement(self):
        AttributionChargeNewFactory(
            attribution__tutor__person__global_id=self.matricule_fgs_enseignant,
            learning_component_year__learning_unit_year=self.learning_unit_year,
        )
        result = self.function_to_test(self.matricule_fgs_enseignant, self.annee)[0]
        self.assertEqual(result.learning_unit_code, self.learning_unit_year.learning_container_year.acronym)
        self.assertEqual(
            result.learning_unit_year,
            self.learning_unit_year.learning_container_year.academic_year.year
        )

    def test_should_renvoyer_detail_attribution(self):
        attribution_charge = AttributionChargeNewFactory(
            attribution__tutor__person__global_id=self.matricule_fgs_enseignant,
            learning_component_year__learning_unit_year=self.learning_unit_year,
        )
        result = self.function_to_test(self.matricule_fgs_enseignant, self.annee)[0]
        self.assertEqual(result.attribution_uuid, attribution_charge.attribution.uuid)
        self.assertEqual(result.last_name, attribution_charge.attribution.tutor.person.last_name)
        self.assertEqual(result.first_name, attribution_charge.attribution.tutor.person.first_name)
        self.assertEqual(result.personal_id_number, attribution_charge.attribution.tutor.person.global_id)
        self.assertEqual(result.function, attribution_charge.attribution.function)

    def test_should_renvoyer_volume_partie_pratique(self):
        AttributionChargeNewFactory(
            attribution__tutor__person__global_id=self.matricule_fgs_enseignant,
            learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES,
            learning_component_year__learning_unit_year=self.learning_unit_year,
            allocation_charge=10.0,
        )
        result = self.function_to_test(self.matricule_fgs_enseignant, self.annee)[0]
        self.assertIsNone(result.lecturing_volume_attributed)
        self.assertEqual(result.practical_volume_attributed, 10.0)

    def test_should_renvoyer_volume_partie_magistrale(self):
        AttributionChargeNewFactory(
            attribution__tutor__person__global_id=self.matricule_fgs_enseignant,
            learning_component_year__type=learning_component_year_type.LECTURING,
            learning_component_year__learning_unit_year=self.learning_unit_year,
            allocation_charge=20.0,
        )
        result = self.function_to_test(self.matricule_fgs_enseignant, self.annee)[0]
        self.assertIsNone(result.practical_volume_attributed)
        self.assertEqual(result.lecturing_volume_attributed, 20.0)
