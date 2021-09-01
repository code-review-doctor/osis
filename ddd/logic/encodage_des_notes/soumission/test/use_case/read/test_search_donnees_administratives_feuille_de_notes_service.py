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

from ddd.logic.encodage_des_notes.soumission.commands import SearchAdressesFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.dtos import DateDTO
from ddd.logic.encodage_des_notes.tests.factory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesSpecifiqueFactory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.inscription_examen import \
    InscriptionExamenTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.deliberation import \
    DeliberationTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class SearchDonneesAdministrativesTest(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2020
        self.numero_session = 2
        self.matricule_enseignant = '00321234'
        self.code_unite_enseignement = 'LDROI1001'
        self.nom_cohorte = 'DROI1BA'

        self.cmd = SearchAdressesFeuilleDeNotesCommand(
            codes_unite_enseignement=[self.code_unite_enseignement],
        )

        self.adresse_feuille_de_notes_repository = AdresseFeuilleDeNotesInMemoryRepository()
        self.adresse_feuille_de_notes_repository.entities.clear()
        self.adresse = AdresseFeuilleDeNotesSpecifiqueFactory()
        self.adresse_feuille_de_notes_repository.save(self.adresse)

        self.periode_encodage_translator = PeriodeEncodageNotesTranslatorInMemory()
        self.inscr_examen_translator = InscriptionExamenTranslatorInMemory()
        self.deliberation_translator = DeliberationTranslatorInMemory()
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            PeriodeEncodageNotesTranslator=lambda: self.periode_encodage_translator,
            AdresseFeuilleDeNotesRepository=lambda: self.adresse_feuille_de_notes_repository,
            InscriptionExamenTranslator=lambda: self.inscr_examen_translator,
            DeliberationTranslator=lambda: self.deliberation_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_should_renvoyer_aucun_resultat(self):
        cmd = SearchAdressesFeuilleDeNotesCommand(codes_unite_enseignement=['EXISTEPAS'])
        result = self.message_bus.invoke(cmd)
        self.assertEqual(result, list())

    @mock.patch("infrastructure.messages_bus.DeliberationTranslator")
    def test_should_renvoyer_aucune_date_deliberation(self, mock_delibe_translator):
        translator = DeliberationTranslatorInMemory()
        translator.search = lambda *args, **kwargs: set()
        mock_delibe_translator.return_value = translator
        result = self.message_bus.invoke(self.cmd)
        dto = list(result)[0]
        self.assertEqual(dto.sigle_formation, self.nom_cohorte)
        self.assertIsNone(dto.date_deliberation)

    def test_should_renvoyer_date_deliberation(self):
        result = self.message_bus.invoke(self.cmd)
        dto = list(result)[0]
        self.assertEqual(dto.sigle_formation, self.nom_cohorte)
        self.assertEqual(dto.date_deliberation, DateDTO(jour=15, mois=6, annee=2020))

    def test_should_renvoyer_contact_feuille_de_notes(self):
        result = self.message_bus.invoke(self.cmd)
        dto = list(result)[0]
        self.assertEqual(dto.contact_feuille_de_notes.nom_cohorte, self.nom_cohorte)
        self.assertEqual(dto.contact_feuille_de_notes.destinataire, 'Faculté de Droit')
        self.assertEqual(dto.contact_feuille_de_notes.rue_numero, 'Rue de la Fac, 19')
        self.assertEqual(dto.contact_feuille_de_notes.code_postal, '1321')
        self.assertEqual(dto.contact_feuille_de_notes.ville, 'Louvain-La-Neuve')
        self.assertEqual(dto.contact_feuille_de_notes.pays, 'Belgique')
        self.assertEqual(dto.contact_feuille_de_notes.telephone, '0106601122')
        self.assertEqual(dto.contact_feuille_de_notes.fax, '0106601123')
        self.assertEqual(dto.contact_feuille_de_notes.email, 'email-fac-droit@email.be')
