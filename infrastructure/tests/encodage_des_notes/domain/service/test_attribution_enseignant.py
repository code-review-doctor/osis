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

from attribution.tests.factories.attribution_class import AttributionClassFactory
from attribution.tests.factories.attribution_new import AttributionNewFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from ddd.logic.encodage_des_notes.soumission.dtos import AttributionEnseignantDTO
from infrastructure.encodage_de_notes.shared_kernel.service.attribution_enseignant import \
    AttributionEnseignantTranslator


class AttributionEnseignantTest(TestCase):  # TODO :: to convert to SimpleTestCase (mock service_bus)

    @classmethod
    def setUpTestData(cls):
        cls.code_unite_enseignement = "LDROI1001"
        cls.annee = 2020
        cls.translator = AttributionEnseignantTranslator()

        cls.attribution_db = AttributionNewFactory(
            learning_container_year__acronym=cls.code_unite_enseignement,
            learning_container_year__academic_year__year=cls.annee,
        )

    def test_should_trouver_attribution_unite_enseignement(self):
        attribution_class = AttributionClassFactory(
            attribution_charge__attribution=self.attribution_db,
            learning_class_year__learning_component_year__learning_unit_year__academic_year__year=self.annee,
            learning_class_year__learning_component_year__learning_unit_year__acronym=self.code_unite_enseignement,
        )
        result = self.translator.search_attributions_enseignant(self.code_unite_enseignement, self.annee)

        expected_result = {self._convert_attribution_db_data_to_dto(self.attribution_db)}
        detail_assertion = "Seule l'attribution à l'unite enseignement doit être renvoyée, pas l'attrib. à la classe"
        attribution_classe = self._convert_class_attribution_db_data_to_dto(attribution_class)
        self.assertNotIn(attribution_classe, result, detail_assertion)
        self.assertSetEqual(expected_result, result, detail_assertion)

    def test_should_trouver_attribution_par_matricule(self):
        result = self.translator.search_attributions_enseignant_par_matricule(
            self.annee,
            self.attribution_db.tutor.person.global_id,
        )

        expected_result = {self._convert_attribution_db_data_to_dto(self.attribution_db)}
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_attribution_pour_une_classe_par_matricule(self):
        attribution_class = AttributionClassFactory(
            learning_class_year__learning_component_year__learning_unit_year__academic_year__year=self.annee,
            learning_class_year__learning_component_year__learning_unit_year__acronym=self.code_unite_enseignement,
        )

        result = self.translator.search_attributions_enseignant_par_matricule(
            self.annee,
            attribution_class.attribution_charge.attribution.tutor.person.global_id,
        )

        expected_result = {
            self._convert_attribution_db_data_to_dto(attribution_class.attribution_charge.attribution),
            self._convert_class_attribution_db_data_to_dto(attribution_class)
        }
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_repartition_classes_par_unite_enseignement(self):
        container = LearningContainerYearFactory()
        attribution_class = AttributionClassFactory(
            attribution_charge__attribution__learning_container_year=container,
            learning_class_year__learning_component_year__learning_unit_year__learning_container_year=container,
            learning_class_year__learning_component_year__learning_unit_year__academic_year=container.academic_year,
            learning_class_year__learning_component_year__learning_unit_year__acronym=container.acronym,
        )
        code_complet_classe = container.acronym + attribution_class.learning_class_year.acronym
        result = self.translator.search_attributions_enseignant(
            code_unite_enseignement=code_complet_classe,
            annee=container.academic_year.year,
        )

        expected_result = {self._convert_class_attribution_db_data_to_dto(attribution_class)}
        attribution_ue = self._convert_attribution_db_data_to_dto(attribution_class.attribution_charge.attribution)
        detail_assertion = "Seule l'attribution à la classe doit être renvoyée, pas l'UE"
        self.assertNotIn(attribution_ue, result, detail_assertion)
        self.assertSetEqual(expected_result, result, detail_assertion)

    def _convert_attribution_db_data_to_dto(self, attribution_db):
        return AttributionEnseignantDTO(
            matricule_fgs_enseignant=attribution_db.tutor.person.global_id,
            code_unite_enseignement=attribution_db.learning_container_year.acronym,
            annee=attribution_db.learning_container_year.academic_year.year,
            nom=attribution_db.tutor.person.last_name,
            prenom=attribution_db.tutor.person.first_name,
        )

    def _convert_class_attribution_db_data_to_dto(self, class_attribution_db):
        attribution_db = class_attribution_db.attribution_charge.attribution
        class_year = class_attribution_db.learning_class_year
        return AttributionEnseignantDTO(
            matricule_fgs_enseignant=attribution_db.tutor.person.global_id,
            code_unite_enseignement='{}{}'.format(
                class_year.learning_component_year.learning_unit_year.acronym,
                class_year.acronym,
            ),
            annee=attribution_db.learning_container_year.academic_year.year,
            nom=attribution_db.tutor.person.last_name,
            prenom=attribution_db.tutor.person.first_name,
        )
