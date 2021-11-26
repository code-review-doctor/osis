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

from ddd.logic.encodage_des_notes.encodage.domain.model._note import NoteManquante
from ddd.logic.encodage_des_notes.soumission.test.factory.note_etudiant import NoteManquanteEtudiantFactory, \
    NoteJustificationSoumiseEtudiantFactory, \
    NoteDejaSoumise
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.inscription_examen import \
    InscriptionExamenTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.signaletique_etudiant import \
    SignaletiqueEtudiantTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.signaletique_personne import \
    SignaletiquePersonneTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.notifier_soumission_notes import \
    NotifierSoumissionNotes, TEMPLATE_MAIL_SOUMISSION_NOTES
from infrastructure.encodage_de_notes.soumission.repository.in_memory.note_etudiant import \
    NoteEtudiantInMemoryRepository


@mock.patch("osis_common.messaging.send_message.send_messages")
class TestNotifierEncodageNotes(SimpleTestCase):

    def setUp(self):
        self.note_etudiant_repo = NoteEtudiantInMemoryRepository()
        self.note_etudiant_repo.entities.clear()
        self.addCleanup(self.note_etudiant_repo.entities.clear)

        self.attribution_translator = AttributionEnseignantTranslatorInMemory()
        self.signaletique_personne_repo = SignaletiquePersonneTranslatorInMemory()
        self.signaletique_etudiant_repo = SignaletiqueEtudiantTranslatorInMemory()
        self.inscr_exam_translator = InscriptionExamenTranslatorInMemory()

        self.notes_ldroi1001 = self.generate_notes_for_ldroi1001()

        self._mock_get_person_id_in_db()

    def _mock_get_person_id_in_db(self):
        patcher_get_person_id = mock.patch(
            'infrastructure.encodage_de_notes.soumission.domain.service.notifier_soumission_notes'
            '.NotifierSoumissionNotes._get_receiver_id'
        )
        mock_get_person_id = patcher_get_person_id.start()
        mock_get_person_id.return_value = 123
        self.addCleanup(patcher_get_person_id.stop)

    def generate_notes_for_ldroi1001(self):
        notes = [
            NoteDejaSoumise(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="11111111",
                nom_cohorte="DROI1BA"
            ),
            NoteDejaSoumise(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="22222222",
                nom_cohorte="DROI1BA"
            ),
            NoteDejaSoumise(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="33333333",
                nom_cohorte="DROI1BA"
            ),
            NoteJustificationSoumiseEtudiantFactory(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="44444444",
                nom_cohorte="DROI1BA",
            ),
            NoteDejaSoumise(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="99999999",
                nom_cohorte="ECGE1BA"
            ),
            NoteDejaSoumise(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="8523645",
                nom_cohorte="ECGE1BA"
            ),
            NoteDejaSoumise(
                entity_id__code_unite_enseignement="LDROI1001",
                entity_id__noma="45896321",
                nom_cohorte="ECGE1BA"
            ),
        ]

        for note in notes:
            self.note_etudiant_repo.save(note)
        return notes

    def test_should_envoyer_aucun_mail_si_aucune_note_encodee(self, mock_send_mail):
        notes_encodees = []

        NotifierSoumissionNotes().notifier(
            notes_encodees,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.inscr_exam_translator,
        )

        self.assertFalse(mock_send_mail.called)

    def test_should_envoyer_mail_soumission_avec_status_notes_restantes_a_encoder(self, mock_send_mail):
        notes_encodees = [self.notes_ldroi1001[0].entity_id]

        note_manquante = NoteManquanteEtudiantFactory(
            entity_id__code_unite_enseignement="LDROI1001",
            entity_id__noma="55555555",
            nom_cohorte="DROI1BA"
        )
        self.note_etudiant_repo.save(note_manquante)

        NotifierSoumissionNotes().notifier(
            notes_encodees,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.inscr_exam_translator,
        )

        args = mock_send_mail.call_args[0][0]
        self.assertIn('Il reste encore des notes à encoder', args['template_base_data']['encoding_status'])

    def test_should_envoyer_mail_soumission_avec_status_toutes_notes_soumises(self, mock_send_mail):
        notes_encodees = [self.notes_ldroi1001[0].entity_id]

        NotifierSoumissionNotes().notifier(
            notes_encodees,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.inscr_exam_translator,
        )

        args = mock_send_mail.call_args[0][0]
        self.assertIn('Toutes les notes ont été soumises.', args['template_base_data']['encoding_status'])

    def test_should_envoyer_mail_soumission_avec_status_toutes_notes_soumises_si_note_manquante_sur_etd_desinscrit(
            self,
            mock_send_mail
    ):
        notes_encodees = [self.notes_ldroi1001[0].entity_id]

        etd_desinscrit = self.notes_ldroi1001[1]
        note_manquante_sur_etd_desinscrit = attr.evolve(etd_desinscrit, note=NoteManquante())
        self.note_etudiant_repo.save(note_manquante_sur_etd_desinscrit)

        NotifierSoumissionNotes().notifier(
            notes_encodees,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.inscr_exam_translator,
        )

        args = mock_send_mail.call_args[0][0]
        self.assertIn(TEMPLATE_MAIL_SOUMISSION_NOTES, args['html_template_ref'])
        self.assertIn('Toutes les notes ont été soumises.', args['template_base_data']['encoding_status'])

    def test_should_afficher_dans_mail_uniquement_note_encodee_et_soumise(self, mock_send_mail):
        notes_encodees_et_soumises = [self.notes_ldroi1001[0].entity_id]

        NotifierSoumissionNotes().notifier(
            notes_encodees_et_soumises,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.inscr_exam_translator,
        )

        args = mock_send_mail.call_args[0][0]
        self.assertEqual(len(notes_encodees_et_soumises), len(args['tables'][0]['data']))
        self.assertEqual(notes_encodees_et_soumises[0].noma, args['tables'][0]['data'][0][2])

    def test_should_injecter_unite_enseignement_et_cohorte_dans_sujet_et_body_du_mail_correction_encodage_complet(
            self,
            mock_send_mail
    ):
        notes_encodees = [self.notes_ldroi1001[0].entity_id]

        NotifierSoumissionNotes().notifier(
            notes_encodees,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.inscr_exam_translator,
        )

        args = mock_send_mail.call_args[0][0]
        self.assertEqual("LDROI1001", args['template_base_data']['learning_unit_name'])
        self.assertEqual("LDROI1001", args['subject_data']['learning_unit_name'])

    def test_should_sort_students_by_removing_accents_and_special_characters(self, mock_send_mail):
        notes_encodees = [
            self.notes_ldroi1001[4].entity_id,
            self.notes_ldroi1001[5].entity_id,
            self.notes_ldroi1001[6].entity_id,
        ]

        NotifierSoumissionNotes().notifier(
            notes_encodees,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.inscr_exam_translator,
        )

        tables_rows = mock_send_mail.call_args[0][0]['tables'][0]['data']
        expected_nom_order = ["Arogan, Adrien", "Déjean, Morge", "De Pierre, Adrién"]
        actual_order = [row[3] for row in tables_rows]
        self.assertListEqual(expected_nom_order, actual_order)
