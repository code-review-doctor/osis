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
from unittest import mock

import attr
from django.test import SimpleTestCase

from ddd.logic.encodage_des_notes.encodage.commands import RechercherNotesCommand
from ddd.logic.encodage_des_notes.encodage.domain.model._note import NOTE_MANQUANTE
from ddd.logic.encodage_des_notes.encodage.test.factory.note_etudiant import NoteManquanteEtudiantFactory, \
    NoteEtudiantChiffreeFactory, NoteEtudiantJustificationFactory
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PasGestionnaireParcoursCohorteException
from infrastructure.encodage_de_notes.encodage.domain.service.in_memory.cohortes_du_gestionnaire import \
    CohortesDuGestionnaireInMemory
from infrastructure.encodage_de_notes.encodage.repository.in_memory.note_etudiant import NoteEtudiantInMemoryRepository
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.periode_encodage_notes import \
    PeriodeEncodageNotesTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.signaletique_etudiant import \
    SignaletiqueEtudiantTranslatorInMemory
from infrastructure.messages_bus import message_bus_instance


class TestRechercherNotes(SimpleTestCase):
    def setUp(self) -> None:
        self.cmd = RechercherNotesCommand(
            noma="",
            nom="",
            prenom="",
            etat="",
            nom_cohorte="",
            matricule_fgs_gestionnaire="22220000"
        )
        self.note_etudiant_repo = NoteEtudiantInMemoryRepository()
        self.note_etudiant_repo.entities.clear()

        self.note_etudiant_repo.save(NoteManquanteEtudiantFactory())
        self.note_etudiant_repo.save(NoteEtudiantChiffreeFactory())
        self.note_etudiant_repo.save(NoteEtudiantJustificationFactory())
        self.note_etudiant_repo.save(NoteEtudiantJustificationFactory())

        self.periode_translator = PeriodeEncodageNotesTranslatorInMemory()
        self.cohorte_gestionnaire_translator = CohortesDuGestionnaireInMemory()
        self.signaletique_etudiant_translator = SignaletiqueEtudiantTranslatorInMemory()
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            PeriodeEncodageNotesTranslator=lambda: self.periode_translator,
            NoteEtudiantGestionnaireRepository=lambda: self.note_etudiant_repo,
            CohortesDuGestionnaireTranslator=lambda: self.cohorte_gestionnaire_translator,
            SignaletiqueEtudiantTranslator=lambda: self.signaletique_etudiant_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_when_aucun_parametres_should_retourne_toutes_les_notes_des_offre_du_gestionnaire(self):
        self.note_etudiant_repo.save(NoteEtudiantJustificationFactory(nom_cohorte="ECGE1BA"))

        result = message_bus_instance.invoke(self.cmd)

        self.assertEqual(len(result), 4)

    def test_when_nom_cohorte_est_donnee_should_retourner_les_notes_de_cette_offre(self):
        cmd = attr.evolve(self.cmd, nom_cohorte="DROI1BA")

        result = message_bus_instance.invoke(cmd)

        self.assertEqual(len(result), 4)

    def test_should_raise_exception_when_nom_cohorte_n_est_pas_une_cohorte_du_gestionnaire(self):
        cmd = attr.evolve(self.cmd, nom_cohorte="ECGE1BA")

        with self.assertRaises(PasGestionnaireParcoursCohorteException):
            message_bus_instance.invoke(cmd)

    def test_should_return_notes_correspondantes_when_justification_est_precise(self):
        note = NoteEtudiantJustificationFactory()
        self.note_etudiant_repo.save(note)

        cmd = attr.evolve(self.cmd, etat=note.note.value.name)

        result = message_bus_instance.invoke(cmd)

        self.assertSetEqual(
            {note_dto.note for note_dto in result},
            {str(note.note.value)}
        )

    def test_should_return_notes_manquantes_when_etat_est_note_manquante(self):
        cmd = attr.evolve(self.cmd, etat=NOTE_MANQUANTE)

        result = message_bus_instance.invoke(cmd)

        self.assertSetEqual(
            {note_dto.note for note_dto in result},
            {""}
        )

    def test_should_return_note_etudiant_correspondant_when_noma_est_donne(self):
        note = NoteManquanteEtudiantFactory(entity_id__noma="45457898")
        self.note_etudiant_repo.save(note)

        cmd = attr.evolve(self.cmd, noma=note.noma)

        result = message_bus_instance.invoke(cmd)

        self.assertListEqual(
            [note_dto.noma for note_dto in result],
            [note.noma]
        )

    def test_should_return_note_etudiant_correspondant_when_nom_est_donne(self):
        note = NoteManquanteEtudiantFactory(entity_id__noma="11111111")
        self.note_etudiant_repo.save(note)

        cmd = attr.evolve(self.cmd, nom="Dupon")

        result = message_bus_instance.invoke(cmd)

        self.assertListEqual(
            [note_dto.noma for note_dto in result],
            [note.noma]
        )

    def test_should_return_note_etudiant_correspondant_when_prenom_est_donne(self):
        note = NoteManquanteEtudiantFactory(entity_id__noma="11111111")
        self.note_etudiant_repo.save(note)

        cmd = attr.evolve(self.cmd, prenom="Marie")

        result = message_bus_instance.invoke(cmd)

        self.assertListEqual(
            [note_dto.noma for note_dto in result],
            [note.noma]
        )

    def test_should_return_notes_correspondantes_when_plusieurs_criteres_sont_selectionnes(self):
        cmd = attr.evolve(self.cmd, nom_cohorte="DROI1BA", etat=NOTE_MANQUANTE)

        result = message_bus_instance.invoke(cmd)

        self.assertEqual(
            len(result),
            1
        )
