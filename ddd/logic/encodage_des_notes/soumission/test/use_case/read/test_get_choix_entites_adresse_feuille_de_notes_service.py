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
import mock
from django.test import SimpleTestCase

from base.models.enums.entity_type import EntityType
from ddd.logic.encodage_des_notes.soumission.commands import GetChoixEntitesAdresseFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.dtos import EntiteDTO
from ddd.logic.shared_kernel.entite.builder.identite_entite_builder import IdentiteEntiteBuilder
from ddd.logic.shared_kernel.entite.tests.factory.entite import INFOEntiteFactory, EPLEntiteFactory, SSTEntiteFactory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.entites_cohorte import \
    EntitesCohorteTranslatorInMemory
from infrastructure.messages_bus import message_bus_instance
from infrastructure.shared_kernel.entite.repository.in_memory.entite import EntiteInMemoryRepository


class TestGetChoixEntitesAdresseFeuilleDeNotes(SimpleTestCase):
    def setUp(self) -> None:
        self.cmd = GetChoixEntitesAdresseFeuilleDeNotesCommand(nom_cohorte='OSIS1BA')

        self.entite_repository = EntiteInMemoryRepository()
        self.entite_repository.entities.clear()
        self.entite_repository.entities.append(INFOEntiteFactory())
        self.entite_repository.entities.append(EPLEntiteFactory())
        self.entite_repository.entities.append(SSTEntiteFactory())

        self.entites_cohorte_translator = EntitesCohorteTranslatorInMemory()
        self.entites_cohorte_translator.datas.clear()

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            EntiteRepository=lambda: self.entite_repository,
            EntitesCohorteTranslator=lambda: self.entites_cohorte_translator
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_return_entites_de_la_cohorte_si_celui_n_a_pas_de_parents_de_type_faculte(self):
        self.entites_cohorte_translator.datas.append(IdentiteEntiteBuilder().build_from_sigle("EPL"))

        result = self.message_bus.invoke(self.cmd)

        expected = [EntiteDTO(sigle="EPL", sigle_parent="SST", type=EntityType.FACULTY)]
        self.assertListEqual(result, expected)

    def test_should_return_entites_de_la_cohorte_avec_son_parent_de_type_de_faculte(self):
        self.entites_cohorte_translator.datas.append(IdentiteEntiteBuilder().build_from_sigle("INFO"))

        result = self.message_bus.invoke(self.cmd)

        expected = [
            EntiteDTO(sigle="INFO", sigle_parent="EPL", type=EntityType.SCHOOL),
            EntiteDTO(sigle="EPL", sigle_parent="SST", type=EntityType.FACULTY)
        ]
        self.assertCountEqual(result, expected)
