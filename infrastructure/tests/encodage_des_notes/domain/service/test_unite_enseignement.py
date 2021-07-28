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
import mock
from django.test import TestCase

from ddd.logic.encodage_des_notes.soumission.dtos import UniteEnseignementDTO
from ddd.logic.learning_unit.dtos import LearningUnitSearchDTO
from infrastructure.encodage_de_notes.soumission.domain.service.unite_enseignement import UniteEnseignementTranslator
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository


class UniteEnseignementTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.code_unite_enseignement = "LDROI1001"
        cls.annee = 2020
        cls.translator = UniteEnseignementTranslator()
        cls.unite_enseignement_repo = LearningUnitRepository()
        cls.fake_dto = LearningUnitSearchDTO(
            year=cls.annee,
            code=cls.code_unite_enseignement,
            full_title="A title",
            type="A type",
            responsible_entity_code="OSIS",
            responsible_entity_title="OSIS Entity"
        )

    @mock.patch('infrastructure.messages_bus.search_learning_units')
    def test_get_should_return_unite_enseignement_dto(self, mock_search):
        mock_search.return_value = [self.fake_dto]
        result = self.translator.get(self.code_unite_enseignement, self.annee)

        expected_result = self._convert_learning_unit_search_dto_to_unit_enseignement_dto(self.fake_dto)
        self.assertEqual(expected_result, result)

    @mock.patch('infrastructure.messages_bus.search_learning_units')
    def test_search_by_codes_should_return_empty_set_if_no_matching_unite_enseignement(self, mock_search):
        mock_search.return_value = []
        result = self.translator.search_by_codes({self.code_unite_enseignement}, self.annee)

        expected_result = set()
        self.assertEqual(expected_result, result)

    @mock.patch('infrastructure.messages_bus.search_learning_units')
    def test_search_by_codes_should_return_set_of_unite_enseignement_dto(self, mock_search):
        mock_search.return_value = [self.fake_dto]
        result = self.translator.search_by_codes({self.code_unite_enseignement}, self.annee)

        expected_result = {self._convert_learning_unit_search_dto_to_unit_enseignement_dto(self.fake_dto)}
        self.assertEqual(expected_result, result)

    def _convert_learning_unit_search_dto_to_unit_enseignement_dto(self, learning_unit_dto):
        return UniteEnseignementDTO(
            annee=learning_unit_dto.year,
            code=learning_unit_dto.code,
            intitule_complet=learning_unit_dto.full_title
        )
