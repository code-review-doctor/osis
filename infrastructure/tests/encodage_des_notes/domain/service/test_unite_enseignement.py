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

from infrastructure.encodage_de_notes.soumission.domain.service.unite_enseignement import UniteEnseignementTranslator
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository


class UniteEnseignementTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.code_unite_enseignement = "LDROI1001"
        cls.annee = 2020
        cls.translator = UniteEnseignementTranslator()
        cls.unite_enseignement_repo = LearningUnitRepository()

    @mock.patch('infrastructure.messages_bus.search_learning_units')
    def test_should_appeler_message_bus(self, mock_search):
        self.translator.get(self.code_unite_enseignement, self.annee)
        self.assertTrue(mock_search.called)
