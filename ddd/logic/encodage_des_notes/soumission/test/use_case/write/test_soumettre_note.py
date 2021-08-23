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

import attr
import mock
from django.test import SimpleTestCase

from ddd.logic.encodage_des_notes.shared_kernel.dtos import DateDTO, PeriodeEncodageNotesDTO
from ddd.logic.encodage_des_notes.soumission.commands import SoumettreNoteCommand
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PasResponsableDeNotesException
from ddd.logic.encodage_des_notes.shared_kernel.validator.exceptions import PeriodeEncodageNotesFermeeException
from ddd.logic.encodage_des_notes.soumission.test.factory.note_etudiant import NoteManquanteEtudiantFactory, \
    NoteChiffreEtudiantFactory
from ddd.logic.encodage_des_notes.soumission.test.factory.responsable_de_notes import \
    ResponsableDeNotesLDROI1001Annee2020Factory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.note_etudiant import \
    NoteEtudiantInMemoryRepository
from infrastructure.encodage_de_notes.soumission.repository.in_memory.responsable_de_notes import \
    ResponsableDeNotesInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class SoumettreNoteTest(SimpleTestCase):

    def setUp(self) -> None:
        self.responsable_notes = ResponsableDeNotesLDROI1001Annee2020Factory()
        self.responsables_notes_repo = ResponsableDeNotesInMemoryRepository()
        self.responsables_notes_repo.save(self.responsable_notes)
        self.matricule_enseignant = self.responsable_notes.matricule_fgs_enseignant

        self.note_etudiant = NoteChiffreEtudiantFactory(entity_id__code_unite_enseignement='LDROI1001')
        self.note_etudiant_repo = NoteEtudiantInMemoryRepository()
        self.note_etudiant_repo.entities.clear()
        self.note_etudiant_repo.save(self.note_etudiant)

        self.cmd = SoumettreNoteCommand(
            code_unite_enseignement=self.note_etudiant.code_unite_enseignement,
            annee_unite_enseignement=self.note_etudiant.annee,
            numero_session=self.note_etudiant.numero_session,
            matricule_fgs_enseignant=self.matricule_enseignant,
            noma_etudiant=self.note_etudiant.noma
        )
        self.__mock_service_bus()

        self.periode_encodage_notes_translator = PeriodeEncodageNotesTranslatorInMemory()

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            NoteEtudiantRepository=lambda: self.note_etudiant_repo,
            ResponsableDeNotesRepository=lambda: self.responsables_notes_repo,
            PeriodeEncodageNotesTranslator=lambda: self.periode_encodage_notes_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_pas_soumettre_si_note_manquante(self):
        note_etudiant = NoteManquanteEtudiantFactory(entity_id__code_unite_enseignement='LDROI1001')
        self.note_etudiant_repo.save(note_etudiant)

        cmd = SoumettreNoteCommand(
            code_unite_enseignement=note_etudiant.code_unite_enseignement,
            annee_unite_enseignement=note_etudiant.annee,
            numero_session=note_etudiant.numero_session,
            noma_etudiant=note_etudiant.noma,
            matricule_fgs_enseignant=self.matricule_enseignant,
        )

        self.message_bus.invoke(cmd)

        note_etudiant_apres_soumettre = self.note_etudiant_repo.get(note_etudiant.entity_id)

        self.assertFalse(note_etudiant_apres_soumettre.est_soumise)

    def test_should_empecher_si_periode_soumission_fermee(self):
        hier = datetime.date.today() - datetime.timedelta(days=1)
        date_dans_le_passe = DateDTO(jour=hier.day, mois=hier.month, annee=hier.year)
        periode_fermee = PeriodeEncodageNotesDTO(
            annee_concernee=self.note_etudiant.annee,
            session_concernee=self.note_etudiant.numero_session,
            debut_periode_soumission=date_dans_le_passe,
            fin_periode_soumission=date_dans_le_passe,
        )
        self.periode_encodage_notes_translator.get = lambda *args: periode_fermee

        with self.assertRaises(PeriodeEncodageNotesFermeeException):
            self.message_bus.invoke(self.cmd)

    def test_should_empecher_si_acune_periode_soumission_trouvee(self):
        aucune_periode_trouvee = None
        self.periode_encodage_notes_translator.get = lambda *args: aucune_periode_trouvee

        with self.assertRaises(PeriodeEncodageNotesFermeeException):
            self.message_bus.invoke(self.cmd)

    def test_should_empecher_si_responsable_de_notes_aucune_unite_enseignement(self):
        matricule_non_responsable = "99999999"
        cmd = attr.evolve(self.cmd, matricule_fgs_enseignant=matricule_non_responsable)

        with self.assertRaises(PasResponsableDeNotesException):
            self.message_bus.invoke(cmd)

    def test_should_empecher_si_pas_responsable_de_notes_unite_enseignement(self):
        cmd = attr.evolve(self.cmd, matricule_fgs_enseignant="124889")

        with self.assertRaises(PasResponsableDeNotesException):
            self.message_bus.invoke(cmd)

    def test_should_soumettre_note(self):
        entity_id = self.message_bus.invoke(self.cmd)

        note_etudiant_retrieved_from_repo = self.note_etudiant_repo.get(entity_id)

        self.assertTrue(note_etudiant_retrieved_from_repo.est_soumise)
