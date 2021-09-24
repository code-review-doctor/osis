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
from django.test import TestCase

from ddd.logic.encodage_des_notes.soumission.test.factory.note_etudiant import NoteChiffreEtudiantFactory, \
    NoteJustificationEtudiantFactory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.signaletique_etudiant import \
    SignaletiqueEtudiantTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.signaletique_personne import \
    SignaletiquePersonneTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.notifier_soumission_notes import NotifierSoumissionNotes
from infrastructure.encodage_de_notes.soumission.repository.in_memory.note_etudiant import \
    NoteEtudiantInMemoryRepository


class TestNotifierEncodageNotes(TestCase):

    def setUp(self):
        self.note_etudiant_repo = NoteEtudiantInMemoryRepository()
        self.note_etudiant_repo.entities.clear()
        self.addCleanup(self.note_etudiant_repo.entities.clear)

        self.attribution_translator = AttributionEnseignantTranslatorInMemory()
        self.signaletique_personne_repo = SignaletiquePersonneTranslatorInMemory()
        self.signaletique_etudiant_repo = SignaletiqueEtudiantTranslatorInMemory()

        self.notes_ldroi1001 = self.generate_notes_for_ldroi1201()

    def generate_notes_for_ldroi1201(self):
        notes = [
            NoteChiffreEtudiantFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="11111111",
                nom_cohorte="DROI1BA"
            ),
            NoteChiffreEtudiantFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="22222222",
                nom_cohorte="DROI1BA"
            ),
            NoteChiffreEtudiantFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="33333333",
                nom_cohorte="DROI1BA"
            ),
            NoteJustificationEtudiantFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="44444444",
                nom_cohorte="DROI1BA"
            ),
            NoteChiffreEtudiantFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="99999999",
                nom_cohorte="ECGE1BA"
            ),
        ]

        for note in notes:
            self.note_etudiant_repo.save(note)
        return notes

    def test_cannot_envoyer_notifications_if_aucune_notes_encodees(self):
        notes_encodees = []

        result = NotifierSoumissionNotes()._get_donnees_email(
            notes_encodees,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
        )

        self.assertListEqual(result, [])

    def test_when_note_est_encodee_should_envoyer_notification_pour_la_meme_cohorte_et_meme_unite_enseignement(self):
        notes_encodees = [self.notes_ldroi1001[0].entity_id]

        result = NotifierSoumissionNotes()._get_donnees_email(
            notes_encodees,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].code_unite_enseignement,
            "LDROI1001"
        )
        self.assertEqual(
            result[0].notes,
            [self.notes_ldroi1001[0]]
        )
