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

from base.models.person import Person
from ddd.logic.encodage_des_notes.encodage.test.factory.gestionnaire_parcours import GestionnaireParcoursDROI1BAFactory
from ddd.logic.encodage_des_notes.encodage.test.factory.note_etudiant import NoteEtudiantChiffreeFactory, \
    NoteEtudiantJustificationFactory
from ddd.logic.encodage_des_notes.shared_kernel.domain.service.i_signaletique_personne import \
    ISignaletiquePersonneTranslator
from infrastructure.encodage_de_notes.encodage.domain.service.notifier_encodage_notes import NotifierEncodageNotes
from infrastructure.encodage_de_notes.encodage.repository.in_memory.note_etudiant import NoteEtudiantInMemoryRepository
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.signaletique_etudiant import \
    SignaletiqueEtudiantTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.signaletique_personne import \
    SignaletiquePersonneTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesInMemoryRepository


class TestNotifierNotes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gestionnaire_parcours_droi1ba = GestionnaireParcoursDROI1BAFactory(
            entity_id__matricule_fgs_gestionnaire="00321234"
        )
        cls.note_etudiant_repo = NoteEtudiantInMemoryRepository()
        cls.note_etudiant_repo.entities.clear()
        cls.addClassCleanup(cls.note_etudiant_repo.entities.clear)

        cls.attribution_translator = AttributionEnseignantTranslatorInMemory()
        cls.signaletique_personne_repo = SignaletiquePersonneTranslatorInMemory()
        cls.signaletique_etudiant_repo = SignaletiqueEtudiantTranslatorInMemory()

        cls.adresse_feuille_de_notes_repo = AdresseFeuilleDeNotesInMemoryRepository()

        cls.notes_ldroi1001 = cls.generate_notes_for_ldroi1201()

    @classmethod
    def generate_notes_for_ldroi1201(cls):
        notes = [
            NoteEtudiantChiffreeFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="11111111",
                nom_cohorte="DROI1BA"
            ),
            NoteEtudiantChiffreeFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="22222222",
                nom_cohorte="DROI1BA"
            ),
            NoteEtudiantChiffreeFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="33333333",
                nom_cohorte="DROI1BA"
            ),
            NoteEtudiantJustificationFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="44444444",
                nom_cohorte="DROI1BA"
            ),
            NoteEtudiantChiffreeFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="99999999",
                nom_cohorte="ECGE1BA"
            ),
        ]

        for note in notes:
            cls.note_etudiant_repo.save(note)
        return notes

    def setUp(self) -> None:
        pass

    def test_cannot_envoyer_notifications_if_aucune_notes_encodees(self):
        notes_encodees = []

        result = NotifierEncodageNotes().notifier(
            notes_encodees,
            self.gestionnaire_parcours_droi1ba,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.adresse_feuille_de_notes_repo
        )

        self.assertListEqual(result, [])

    def test_when_note_est_encodee_should_envoyer_notification_pour_la_meme_cohorte_et_meme_unite_enseignement(self):
        notes_encodees = [self.notes_ldroi1001[0].entity_id]

        result = NotifierEncodageNotes().notifier(
            notes_encodees,
            self.gestionnaire_parcours_droi1ba,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.adresse_feuille_de_notes_repo
        )

        self.assertEqual(len(result), 1)

        mail_data = result[0]
        self.assertDictEqual(
            mail_data.subject_data,
            {
                'learning_unit_acronym': "LDROI1001",
                'offer_acronym': "DROI1BA"
            }
        )
        self.assertDictEqual(
            mail_data.template_base_data,
            {
                'learning_unit_acronym': "LDROI1001",
                'offer_acronym': "DROI1BA"
            }
        )
        self.assertEqual(mail_data.html_template_ref, 'assessments_all_scores_by_pgm_manager_html')
        self.assertEqual(mail_data.txt_template_ref, 'assessments_all_scores_by_pgm_manager_txt')
        self.assertListEqual(
            [cc.email for cc in mail_data.cc],
            ["charles.smith@email.com"]
        )
        self.assertListEqual(
            [receiver["receiver_email"] for receiver in mail_data.receivers],
            ["charles.smith@email.com"]
        )
        self.assertEqual(
            len(mail_data.table),
            4
        )
