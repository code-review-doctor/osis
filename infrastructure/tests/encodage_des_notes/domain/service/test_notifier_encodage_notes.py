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
from ddd.logic.encodage_des_notes.encodage.test.factory.gestionnaire_parcours import GestionnaireParcoursDROI1BAFactory
from ddd.logic.encodage_des_notes.encodage.test.factory.note_etudiant import NoteEtudiantChiffreeFactory, \
    NoteEtudiantJustificationFactory, NoteManquanteEtudiantFactory
from infrastructure.encodage_de_notes.encodage.domain.service.notifier_encodage_notes import NotifierEncodageNotes, \
    ENCODAGE_COMPLET_MAIL_TEMPLATE, CORRECTION_ENCODAGE_COMPLET_MAIL_TEMPLATE
from infrastructure.encodage_de_notes.encodage.repository.in_memory.note_etudiant import NoteEtudiantInMemoryRepository
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.attribution_enseignant import \
    AttributionEnseignantTranslatorInMemory
from infrastructure.encodage_de_notes.shared_kernel.service.in_memory.signaletique_etudiant import \
    SignaletiqueEtudiantTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.domain.service.in_memory.signaletique_personne import \
    SignaletiquePersonneTranslatorInMemory
from infrastructure.encodage_de_notes.soumission.repository.in_memory.adresse_feuille_de_notes import \
    AdresseFeuilleDeNotesInMemoryRepository


@mock.patch("osis_common.messaging.send_message.send_messages")
class TestEnvoyerMailEncodageComplet(SimpleTestCase):

    def setUp(self):
        self.gestionnaire_parcours_droi1ba = GestionnaireParcoursDROI1BAFactory(
            entity_id__matricule_fgs_gestionnaire="00321234"
        )
        self.note_etudiant_repo = NoteEtudiantInMemoryRepository()
        self.note_etudiant_repo.entities.clear()
        self.addCleanup(self.note_etudiant_repo.entities.clear)

        self.attribution_translator = AttributionEnseignantTranslatorInMemory()
        self.signaletique_personne_repo = SignaletiquePersonneTranslatorInMemory()
        self.signaletique_etudiant_repo = SignaletiqueEtudiantTranslatorInMemory()

        self.adresse_feuille_de_notes_repo = AdresseFeuilleDeNotesInMemoryRepository()

        self.notes_ldroi1001 = self.generate_notes_for_ldroi1201()

        self._mock_get_person_id_in_db()

    def _mock_get_person_id_in_db(self):
        patcher_get_person_id = mock.patch(
            'infrastructure.encodage_de_notes.encodage.domain.service.notifier_encodage_notes.NotifierEncodageNotes._get_receiver_id'
        )
        mock_get_person_id = patcher_get_person_id.start()
        mock_get_person_id.return_value = 123
        self.addCleanup(patcher_get_person_id.stop)

    def generate_notes_for_ldroi1201(self):
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
            # NoteManquanteEtudiantFactory(
            #     entity_id__code_unite_enseignement="LDROI1001",
            #     entity_id__noma="88888888",
            #     nom_cohorte="ECGE1BA"
            # ),
        ]

        for note in notes:
            self.note_etudiant_repo.save(note)
        return notes

    def test_should_not_envoyer_notifications_si_aucune_notes_encodees(self, mock_send_mail):
        notes_encodees = []

        NotifierEncodageNotes().notifier(
            notes_encodees,
            [],
            self.gestionnaire_parcours_droi1ba,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.adresse_feuille_de_notes_repo
        )
        self.assertFalse(mock_send_mail.called)

    def test_should_not_envoyer_mail_si_encodage_incomplet_apres_encodage(self, mock_send_mail):
        note_manquante = NoteManquanteEtudiantFactory(
            entity_id__code_unite_enseignement="LDROI1001",
            entity_id__noma="55555555",
            nom_cohorte="DROI1BA"
        )
        self.note_etudiant_repo.save(note_manquante)

        notes_encodees = [self.notes_ldroi1001[0].entity_id]

        NotifierEncodageNotes().notifier(
            notes_encodees,
            [],
            self.gestionnaire_parcours_droi1ba,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.adresse_feuille_de_notes_repo
        )

        self.assertFalse(mock_send_mail.called)

    def test_should_not_envoyer_mail_si_encodage_deja_complet_avant_encodage(self, mock_send_mail):
        notes_encodees = [self.notes_ldroi1001[0].entity_id]

        cohortes_dont_encodage_est_incomplet = []
        NotifierEncodageNotes().notifier(
            notes_encodees,
            cohortes_dont_encodage_est_incomplet,
            self.gestionnaire_parcours_droi1ba,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.adresse_feuille_de_notes_repo,
        )
        args = mock_send_mail.call_args[0][0]
        self.assertNotIn(ENCODAGE_COMPLET_MAIL_TEMPLATE, args['html_template_ref'])
        self.assertIn(CORRECTION_ENCODAGE_COMPLET_MAIL_TEMPLATE, args['html_template_ref'])

    def test_should_envoyer_mail_si_encodage_incomplet_avant_encodage_et_complet_apres_encodage(self, mock_send_mail):
        notes_encodees = [self.notes_ldroi1001[0].entity_id]

        NotifierEncodageNotes().notifier(
            notes_encodees,
            [('LDROI1001', 'DROI1BA')],
            self.gestionnaire_parcours_droi1ba,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.adresse_feuille_de_notes_repo,
        )
        args = mock_send_mail.call_args[0][0]
        self.assertIn(ENCODAGE_COMPLET_MAIL_TEMPLATE, args['html_template_ref'])
        self.assertNotIn(CORRECTION_ENCODAGE_COMPLET_MAIL_TEMPLATE, args['html_template_ref'])

    def test_when_note_est_encodee_should_envoyer_notification_pour_la_meme_cohorte_et_meme_unite_enseignement(
            self,
            mock_send_mail
    ):
        notes_encodees = [self.notes_ldroi1001[0].entity_id]

        NotifierEncodageNotes().notifier(
            notes_encodees,
            [('LDROI1001', 'DROI1BA')],
            self.gestionnaire_parcours_droi1ba,
            self.note_etudiant_repo,
            self.attribution_translator,
            self.signaletique_personne_repo,
            self.signaletique_etudiant_repo,
            self.adresse_feuille_de_notes_repo,
        )

        args = mock_send_mail.call_args[0][0]
        self.assertEqual("LDROI1001", args['template_base_data']['learning_unit_acronym'])
        self.assertEqual("DROI1BA", args['template_base_data']['offer_acronym'])
        self.assertEqual(4, len(args['tables'][0]['data']['data']))
