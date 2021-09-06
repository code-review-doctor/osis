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
from unittest import mock

from django.test import SimpleTestCase

from ddd.logic.learning_unit.commands import SearchDetailClassesEffectivesCommand
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository
from infrastructure.messages_bus import message_bus_instance


class SearchDetailClassesEffectivesTest(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2020
        self.code_unite_enseignement = 'LDROI1001'
        self.lettre_classe = 'A'
        self.repository = EffectiveClassRepository()
        self.cmd = SearchDetailClassesEffectivesCommand(
            codes_classes={self.code_unite_enseignement + self.lettre_classe},
            annee=self.annee,
        )

    @mock.patch('infrastructure.messages_bus.EffectiveClassRepository.search_dtos')
    def test_should_tester_via_repository(self, mock_search_dtos):
        """
        Pas de unit test sur le use case car appel direct au repository, sans logique métier.
        Tous les tests sont donc implémentés sur le repository.
        """
        mock_search_dtos.return_value = []
        message_bus_instance.invoke(self.cmd)
        self.assertTrue(mock_search_dtos.called)
