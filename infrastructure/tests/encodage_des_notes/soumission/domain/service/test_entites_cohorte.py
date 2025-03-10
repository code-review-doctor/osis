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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from ddd.logic.encodage_des_notes.soumission.domain.service.i_entites_cohorte import EntitesCohorteDTO
from ddd.logic.shared_kernel.entite.builder.identite_entite_builder import IdentiteEntiteBuilder
from infrastructure.encodage_de_notes.soumission.domain.service.entites_cohorte import EntitesCohorteTranslator


class TestEntitesCohorte(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.info = EntityVersionFactory(acronym="INFO")
        cls.drt = EntityVersionFactory(acronym="DRT")

        cls.sinf1ba = EducationGroupYearFactory(
            acronym="SINF1BA",
            academic_year__current=True,
            management_entity=cls.info.entity,
            administration_entity=cls.drt.entity
        )

        cls.annee = cls.sinf1ba.academic_year.year

    def setUp(self) -> None:
        self.translator = EntitesCohorteTranslator()

    def test_should_return_dtos_if_matching_nom_cohorte(self):
        result = self.translator.search_entite_administration_et_gestion("SINF1BA", self.annee)

        expected = EntitesCohorteDTO(
            administration=IdentiteEntiteBuilder().build_from_sigle("DRT"),
            gestion=IdentiteEntiteBuilder().build_from_sigle("INFO")
        )
        self.assertEqual(result, expected)

    def test_should_return_empty_list_if_no_matching_nom_cohorte(self):
        EducationGroupYearFactory(
            acronym="ECGE1BA",
            academic_year__current=True,
        )
        result = self.translator.search_entite_administration_et_gestion("ECGE1BA", self.annee)

        expected = EntitesCohorteDTO(
            administration=None,
            gestion=None
        )
        self.assertEqual(result, expected)
