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
import datetime
from unittest import mock

from django.test import SimpleTestCase

from base.models.enums.peps_type import PepsTypes
from ddd.logic.encodage_des_notes.soumission.commands import GetFeuilleDeNotesCommand, \
    SearchAdressesFeuilleDeNotesCommand
from ddd.logic.encodage_des_notes.soumission.dtos import DateDTO, InscriptionExamenDTO, EnseignantDTO, \
    AttributionEnseignantDTO, AdresseDTO
from ddd.logic.encodage_des_notes.tests.factory._note_etudiant import NoteManquanteEtudiantFactory
from ddd.logic.encodage_des_notes.tests.factory.feuille_de_notes import FeuilleDeNotesAvecUneSeuleNoteManquante
from ddd.logic.encodage_des_notes.tests.factory.responsable_de_notes import ResponsableDeNotesLDROI1001Annee2020Factory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.deliberation import \
    DeliberationTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.inscription_examen import \
    InscriptionExamenTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.periode_soumission_notes import \
    PeriodeSoumissionNotesTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.signaletique_etudiant import \
    SignaletiqueEtudiantTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.signaletique_personne import \
    SignaletiquePersonneTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.unite_enseignement import \
    UniteEnseignementTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.feuille_de_notes import \
    FeuilleDeNotesInMemoryRepository
from infrastructure.encodage_de_notes.soumission.repository.in_memory.responsable_de_notes import \
    ResponsableDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class SearchDonneesAdministrativesTest(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2020
        self.numero_session = 2
        self.matricule_enseignant = '00321234'
        self.code_unite_enseignement = 'LDROI1001'
        self.nom_cohorte = 'DROI1BA'

        self.resp_notes_repository = ResponsableDeNotesInMemoryRepository()
        self.responsable_de_notes = ResponsableDeNotesLDROI1001Annee2020Factory(
            entity_id__matricule_fgs_enseignant=self.matricule_enseignant)
        self.resp_notes_repository.save(self.responsable_de_notes)

        self.cmd = SearchAdressesFeuilleDeNotesCommand(
            codes_unite_enseignement=[self.code_unite_enseignement],
        )

        self.periode_soumission_translator = PeriodeSoumissionNotesTranslatorInMemory()
        self.inscr_examen_translator = InscriptionExamenTranslatorInMemory()
        self.adresse_feuille_notes_translator = AdresseFeuilleDeNotesTranslatorInMemory()
        self.deliberation_translator = DeliberationTranslatorInMemory()
        self.signaletique_translator = SignaletiquePersonneTranslatorInMemory()
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            PeriodeSoumissionNotesTranslator=lambda: self.periode_soumission_translator,
            AdresseFeuilleDeNotesTranslator=lambda: self.adresse_feuille_notes_translator,
            SignaletiquePersonneTranslator=lambda: self.signaletique_translator,
            InscriptionExamenTranslator=lambda: self.inscr_examen_translator,
            ResponsableDeNotesRepository=lambda: self.resp_notes_repository,
            DeliberationTranslator=lambda: self.deliberation_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_should_renvoyer_aucun_resultat(self):
        cmd = SearchAdressesFeuilleDeNotesCommand(codes_unite_enseignement=['EXISTEPAS'])
        result = self.message_bus.invoke(cmd)
        self.assertEqual(result, list())

    def test_should_renvoyer_date_deliberation(self):
        result = self.message_bus.invoke(self.cmd)
        dto = list(result)[0]
        self.assertEqual(dto.sigle_formation, self.nom_cohorte)
        self.assertEqual(dto.date_deliberation, DateDTO(jour=15, mois=6, annee=2020))

    def test_should_renvoyer_contact_responsable_notes(self):
        result = self.message_bus.invoke(self.cmd)
        dto = list(result)[0]
        self.assertEqual(dto.contact_responsable_notes.matricule_fgs, self.matricule_enseignant)
        self.assertEqual(dto.contact_responsable_notes.email, "charles.smith@email.com")
        expected_address = AdresseDTO(
            code_postal='1410',
            ville='Waterloo',
            rue_numero_boite='Rue de Waterloo, 123',
        )
        self.assertEqual(dto.contact_responsable_notes.adresse_professionnelle, expected_address)

    def test_should_renvoyer_aucun_contact_responsable_notes(self):
        self.resp_notes_repository.delete(self.responsable_de_notes.entity_id)
        result = self.message_bus.invoke(self.cmd)
        dto = list(result)[0]
        self.assertIsNone(dto.contact_responsable_notes)
        self.resp_notes_repository.save(self.responsable_de_notes)

    def test_should_renvoyer_contact_feuille_de_notes(self):
        result = self.message_bus.invoke(self.cmd)
        dto = list(result)[0]
        self.assertEqual(dto.contact_feuille_de_notes.nom_cohorte, self.nom_cohorte)
        self.assertEqual(dto.contact_feuille_de_notes.destinataire, 'Faculté de Droit')
        self.assertEqual(dto.contact_feuille_de_notes.rue_et_numero, 'Rue de la Fac, 19')
        self.assertEqual(dto.contact_feuille_de_notes.code_postal, '1321')
        self.assertEqual(dto.contact_feuille_de_notes.ville, 'Louvain-La-Neuve')
        self.assertEqual(dto.contact_feuille_de_notes.pays, 'Belgique')
        self.assertEqual(dto.contact_feuille_de_notes.telephone, '0106601122')
        self.assertEqual(dto.contact_feuille_de_notes.fax, '0106601123')
        self.assertEqual(dto.contact_feuille_de_notes.email, 'email-fac-droit@email.be')
