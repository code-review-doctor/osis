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

from ddd.logic.encodage_des_notes.soumission.commands import EncoderAdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.model.adresse_feuille_de_notes import IdentiteAdresseFeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    AdressePremiereAnneeDeBachelierIdentiqueAuBachlierException, EntiteNonValidePourAdresseException
from ddd.logic.encodage_des_notes.tests.factory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesBaseeSurEntiteFactory
from ddd.logic.shared_kernel.entite.builder.identite_entite_builder import IdentiteEntiteBuilder
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.entites_cohorte import \
    EntitesCohorteTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance
from infrastructure.shared_kernel.entite.repository.in_memory.entite import EntiteInMemoryRepository


class TestEncoderAddressFeuilleDeNotes(SimpleTestCase):
    def setUp(self) -> None:
        self.cmd = EncoderAdresseFeuilleDeNotes(
            nom_cohorte="SINF1BA",
            entite="",
            destinataire="",
            rue_numero="",
            code_postal="",
            ville="",
            pays="",
            telephone="",
            fax="",
            email="",
        )

        self.repo = AdresseFeuilleDeNotesInMemoryRepository()
        self.repo.entities.clear()

        self.entite_repository = EntiteInMemoryRepository()
        self.entite_repository.entities.clear()

        self.entites_cohorte_translator = EntitesCohorteTranslatorInMemory()
        self.entites_cohorte_translator.datas.clear()
        self.entites_cohorte_translator.datas.append(IdentiteEntiteBuilder().build_from_sigle("EPL"))

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            AdresseFeuilleDeNotesRepository=lambda: self.repo,
            EntiteRepository=lambda: self.entite_repository,
            EntitesCohorteTranslator=lambda: self.entites_cohorte_translator
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_ne_peut_pas_encoder_la_meme_entite_que_le_bachelier_pour_la_premiere_annee_de_bachelier(self):
        adresse_bachelier = AdresseFeuilleDeNotesBaseeSurEntiteFactory()
        self.repo.save(adresse_bachelier)

        cmd = attr.evolve(
            self.cmd,
            nom_cohorte=adresse_bachelier.nom_cohorte.replace('1BA', '11BA'),
            entite=adresse_bachelier.entite
        )

        with self.assertRaises(AdressePremiereAnneeDeBachelierIdentiqueAuBachlierException):
            message_bus_instance.invoke(cmd)

    def test_encode_adresse_de_la_commande(self):
        result = message_bus_instance.invoke(self.cmd)

        self.assertIsInstance(result, IdentiteAdresseFeuilleDeNotes)
        self.assertEqual(result.nom_cohorte, self.cmd.nom_cohorte)
        self.assertTrue(
            self.repo.get(result)
        )

    def test_ne_peut_pas_encoder_une_entite_ne_faisant_pas_partie_des_choix_possibles(self):
        cmd = attr.evolve(self.cmd, entite="OSIS")

        with self.assertRaises(EntiteNonValidePourAdresseException):
            message_bus_instance.invoke(cmd)
