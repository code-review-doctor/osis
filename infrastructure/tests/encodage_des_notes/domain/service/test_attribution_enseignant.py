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

from attribution.tests.factories.attribution_new import AttributionNewFactory
from ddd.logic.encodage_des_notes.soumission.dtos import AttributionEnseignantDTO
from infrastructure.encodage_de_notes.soumission.domain.service.attribution_enseignant import \
    AttributionEnseignantTranslator


class AttributionEnseignantTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.matricule_fgs_enseignant = "00323214"
        cls.annee = 2020
        cls.translator = AttributionEnseignantTranslator()

    def test_should_trouver_attribution_unite_enseignement(self):
        AttributionNewFactory()
        attribution_db = AttributionNewFactory(
            tutor__person__global_id=self.matricule_fgs_enseignant,
            learning_container_year__academic_year__year=self.annee,
        )
        result = self.translator.search_attributions_enseignant(self.matricule_fgs_enseignant, self.annee)
        self.assertEqual(len(result), 1)
        expected_result = {
            AttributionEnseignantDTO(
                code_unite_enseignement=attribution_db.learning_container_year.acronym,
                annee=self.annee,
            )
        }
        self.assertSetEqual(expected_result, result)

    def test_should_trouver_repartition_classes(self):
        raise NotImplementedError  # TODO :: en attente du domaine 'effective_class_repartition'
