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
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from osis_history.utilities import get_history_entries

from base.tests.factories.person import PersonFactory
from ddd.logic.encodage_des_notes.soumission.test.factory.note_etudiant import NoteChiffreEtudiantFactory
from infrastructure.encodage_de_notes.soumission.domain.service import historiser_notes
from infrastructure.encodage_de_notes.soumission.domain.service.historiser_notes import HistoriserNotes


class TestHistoriserNotes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = PersonFactory(global_id="32165498")

        cls.note = NoteChiffreEtudiantFactory()
        cls.history_uuid = historiser_notes.get_history_identity(
            code_unite_enseignement=cls.note.code_unite_enseignement,
            annee_academique=cls.note.annee,
            numero_session=cls.note.numero_session
        )

    def test_should_sauver_une_entree_historique_encodage(self):
        HistoriserNotes.historiser_encodage(self.author.global_id, notes_encodees=[self.note])

        history_entries = get_history_entries(object_uuid=self.history_uuid)
        self.assertEqual(len(history_entries), 1)

        with translation.override('fr_BE'):
            scores_with_noma = str(_("(Noma: %(noma)s, Score: %(score)s)") % {
                'noma': self.note.noma,
                'score': str(self.note.note)
            })
            expected_message_fr = str(_("The following scores %(scores_with_noma)s has been encoded") % {
                'scores_with_noma': scores_with_noma
            })
        self.assertEqual(history_entries[0].message_fr, expected_message_fr)

        with translation.override('en'):
            scores_with_noma = str(_("(Noma: %(noma)s, Score: %(score)s)") % {
                'noma': self.note.noma,
                'score': str(self.note.note)
            })
            expected_message_en = str(_("The following scores %(scores_with_noma)s has been encoded") % {
                'scores_with_noma': scores_with_noma
            })
        self.assertEqual(history_entries[0].message_en, expected_message_en)

    def test_should_sauver_une_entree_historique_soumission(self):
        HistoriserNotes.historiser_soumission(self.author.global_id, notes_soumises=[self.note])

        history_entries = get_history_entries(object_uuid=self.history_uuid)
        self.assertEqual(len(history_entries), 1)

        with translation.override('fr_BE'):
            scores_with_noma = str(_("(Noma: %(noma)s, Score: %(score)s)") % {
                'noma': self.note.noma,
                'score': str(self.note.note)
            })
            expected_message_fr = str(_("The following scores %(scores_with_noma)s has been submitted") % {
                'scores_with_noma': scores_with_noma
            })
        self.assertEqual(history_entries[0].message_fr, expected_message_fr)

        with translation.override('en'):
            scores_with_noma = str(_("(Noma: %(noma)s, Score: %(score)s)") % {
                'noma': self.note.noma,
                'score': str(self.note.note)
            })
            expected_message_en = str(_("The following scores %(scores_with_noma)s has been submitted") % {
                'scores_with_noma': scores_with_noma
            })
        self.assertEqual(history_entries[0].message_en, expected_message_en)
