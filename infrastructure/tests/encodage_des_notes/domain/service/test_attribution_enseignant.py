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
from unittest import skip

from django.test import TestCase

from attribution.tests.factories.attribution_class import AttributionClassFactory
from attribution.tests.factories.attribution_new import AttributionNewFactory
from ddd.logic.encodage_des_notes.soumission.dtos import AttributionEnseignantDTO
from infrastructure.encodage_de_notes.shared_kernel.service.attribution_enseignant import \
    AttributionEnseignantTranslator


class AttributionEnseignantTest(TestCase):

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
        result = self.translator.search_attributions_enseignant(self.code_unite_enseignement, self.annee)

        expected_result = {self._convert_attribution_db_data_to_dto(self.attribution_db)}
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_attribution_par_matricule(self):
        result = self.translator.search_attributions_enseignant_par_matricule(
            self.annee,
            self.attribution_db.tutor.person.global_id,
        )

        expected_result = {self._convert_attribution_db_data_to_dto(self.attribution_db)}
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_attribution_pour_une_classe_par_matricule(self):
        attribution_class = AttributionClassFactory()

        result = self.translator.search_attributions_enseignant_par_matricule(
            self.annee,
            attribution_class.attribution_charge.attribution.tutor.person.global_id,
        )

        expected_result = {
            self._convert_attribution_db_data_to_dto(attribution_class.attribution_charge.attribution),
            self._convert_class_attribution_db_data_to_dto(attribution_class)
        }
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_repartition_classes(self):
        raise NotImplementedError  # TODO :: en attente du domaine 'effective_class_repartition'

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
