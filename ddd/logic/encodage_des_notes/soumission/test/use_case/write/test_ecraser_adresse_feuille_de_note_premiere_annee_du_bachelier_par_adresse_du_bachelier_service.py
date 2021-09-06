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

from ddd.logic.encodage_des_notes.soumission.commands import EcraserAdresseFeuilleDeNotesPremiereAnneeDeBachelier
from ddd.logic.encodage_des_notes.tests.factory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesSpecifiqueFactory, \
    AdresseFeuilleDeNotesBaseeSurEntiteFactory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance
from testing.assertions import assert_attrs_instances_are_equal


class TestEcraserAdresseFeuilleDeNotePremiereAnneeDuBachlierParAdresseDuBachelier(SimpleTestCase):
    def setUp(self) -> None:
        self.cmd = EcraserAdresseFeuilleDeNotesPremiereAnneeDeBachelier(
            nom_cohorte="DROI11BA",
        )

        self.repo = AdresseFeuilleDeNotesInMemoryRepository()
        self.repo.entities.clear()

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            AdresseFeuilleDeNotesRepository=lambda: self.repo,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_avoir_meme_adresse_entre_bachelier_et_premiere_annee_de_bachelier(self):
        adresse_bachelier = AdresseFeuilleDeNotesSpecifiqueFactory()
        adresse_premiere_annee_de_bachelier = AdresseFeuilleDeNotesBaseeSurEntiteFactory(
            entity_id__nom_cohorte="DROI11BA"
        )
        self.repo.save(adresse_bachelier)
        self.repo.save(adresse_premiere_annee_de_bachelier)

        result = message_bus_instance.invoke(self.cmd)

        adresse_sauvegardee = self.repo.get(result)

        assert_attrs_instances_are_equal(
            adresse_bachelier,
            adresse_sauvegardee,
            exclude=["entity_id"]
        )
