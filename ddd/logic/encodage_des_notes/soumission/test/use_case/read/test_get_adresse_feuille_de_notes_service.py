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
import attr
import mock
from django.test import SimpleTestCase

from ddd.logic.encodage_des_notes.soumission.commands import GetAdresseFeuilleDeNotesServiceCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import AdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import AdresseFeuilleDeNotesDTO
from ddd.logic.encodage_des_notes.tests.factory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesSpecifiqueFactory, \
    AdresseFeuilleDeNotesBaseeSurEntiteFactory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestGetAdresseFeuilleDeNotesService(SimpleTestCase):
    def setUp(self) -> None:
        self.repository = AdresseFeuilleDeNotesInMemoryRepository()
        self.addCleanup(self.repository.reset)

        self.cmd = GetAdresseFeuilleDeNotesServiceCommand(
            nom_cohorte="SINF1BA"
        )
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            AdresseFeuilleDeNotesRepository=lambda: self.repository,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_return_dto(self):
        adresse = AdresseFeuilleDeNotesSpecifiqueFactory()
        cmd = attr.evolve(self.cmd, nom_cohorte=adresse.nom_cohorte)
        self.repository.save(adresse)

        result = message_bus_instance.invoke(cmd)
        self.assert_dto_corresponds_to_adress(
            result,
            adresse,
        )

    def test_should_base_value_on_entity_if_adresse_est_basee_sur_entite(self):
        adresse = AdresseFeuilleDeNotesBaseeSurEntiteFactory()
        self.repository.save(adresse)

        cmd = attr.evolve(self.cmd, nom_cohorte=adresse.nom_cohorte)

        result = message_bus_instance.invoke(cmd)
        self.assert_dto_corresponds_to_adress(
            result,
            adresse,
        )

    def assert_dto_corresponds_to_adress(
            self,
            dto_obj: AdresseFeuilleDeNotesDTO,
            adresse: AdresseFeuilleDeNotes,
    ):
        self.assertEqual(dto_obj.nom_cohorte, adresse.nom_cohorte)
        self.assertEqual(dto_obj.entite, adresse.sigle_entite)
        self.assertEqual(dto_obj.destinataire, adresse.destinataire)
        self.assertEqual(dto_obj.rue_numero, adresse.rue_numero)
        self.assertEqual(dto_obj.code_postal, adresse.code_postal)
        self.assertEqual(dto_obj.ville, adresse.ville)
        self.assertEqual(dto_obj.pays, adresse.pays)
        self.assertEqual(dto_obj.telephone, adresse.telephone)
        self.assertEqual(dto_obj.fax, adresse.fax)
        self.assertEqual(dto_obj.email, adresse.email)
