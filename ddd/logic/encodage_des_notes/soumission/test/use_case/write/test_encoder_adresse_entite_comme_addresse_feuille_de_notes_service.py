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

from ddd.logic.encodage_des_notes.soumission.commands import EncoderAdresseEntiteCommeAdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    AdressePremiereAnneeDeBachelierIdentiqueAuBachlierException, EntiteNonValidePourAdresseException
from ddd.logic.encodage_des_notes.tests.factory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesBaseeSurEntiteFactory
from ddd.logic.shared_kernel.entite.builder.identite_entite_builder import IdentiteEntiteBuilder
from ddd.logic.shared_kernel.entite.tests.factory.entiteucl import EPLEntiteFactory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.entites_cohorte import \
    EntitesCohorteTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance
from infrastructure.shared_kernel.entite.repository.in_memory.entiteucl import EntiteUCLInMemoryRepository


class TestEncoderAddressEntiteCommeAdresseFeuilleDeNotes(SimpleTestCase):
    def setUp(self) -> None:
        self.cmd = EncoderAdresseEntiteCommeAdresseFeuilleDeNotes(
            nom_cohorte="SINF1BA",
            entite="EPL",
            email="temp@temp.com",
        )

        self.repo = AdresseFeuilleDeNotesInMemoryRepository()
        self.repo.entities.clear()

        self.entite_repository = EntiteUCLInMemoryRepository()
        self.entite_repository.entities.clear()
        self.epl_entite = EPLEntiteFactory()
        self.entite_repository.entities.append(EPLEntiteFactory())

        self.entites_cohorte_translator = EntitesCohorteTranslatorInMemory()
        self.entites_cohorte_translator.datas.clear()
        self.entites_cohorte_translator.datas.append(IdentiteEntiteBuilder().build_from_sigle("EPL"))

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            AdresseFeuilleDeNotesRepository=lambda: self.repo,
            EntiteUCLRepository=lambda: self.entite_repository,
            EntitesCohorteTranslator=lambda: self.entites_cohorte_translator
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_cannot_encoder_la_meme_entite_que_le_bachelier_pour_la_premiere_annee_de_bachelier(self):
        adresse_bachelier = AdresseFeuilleDeNotesBaseeSurEntiteFactory()
        self.repo.save(adresse_bachelier)

        cmd = attr.evolve(
            self.cmd,
            nom_cohorte=adresse_bachelier.nom_cohorte.replace('1BA', '11BA'),
            entite=adresse_bachelier.sigle_entite
        )

        with self.assertRaises(AdressePremiereAnneeDeBachelierIdentiqueAuBachlierException):
            message_bus_instance.invoke(cmd)

    def test_cannot_encoder_une_entite_ne_faisant_pas_partie_de_la_cohorte(self):
        cmd = attr.evolve(self.cmd, entite="OSIS")

        with self.assertRaises(EntiteNonValidePourAdresseException):
            message_bus_instance.invoke(cmd)

    def test_should_encoder_valeur_adresse_de_entite(self):
        result = message_bus_instance.invoke(self.cmd)

        adresse = self.repo.get(result)
        self.assertEqual(adresse.email, self.cmd.email)
        self.assertEqual(adresse.sigle_entite, self.cmd.entite)
        self.assertEqual(adresse.rue_numero, self.epl_entite.adresse.rue_numero)
        self.assertEqual(adresse.code_postal, self.epl_entite.adresse.code_postal)
        self.assertEqual(adresse.ville, self.epl_entite.adresse.ville)
        self.assertEqual(adresse.pays, self.epl_entite.adresse.pays)
        self.assertEqual(adresse.telephone, self.epl_entite.adresse.telephone)
        self.assertEqual(adresse.fax, self.epl_entite.adresse.fax)

    def test_should_encoder_aussi_pour_la_premiere_annee_de_bachelier_when_encode_pour_bachelier(self):
        result = message_bus_instance.invoke(self.cmd)

        identite_11ba = attr.evolve(result, nom_cohorte=self.cmd.nom_cohorte.replace("1BA", "11BA"))
        self.assertTrue(self.repo.get(identite_11ba))
