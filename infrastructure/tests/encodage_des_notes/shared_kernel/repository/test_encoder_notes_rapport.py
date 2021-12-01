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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import uuid

from django.test import TestCase

from ddd.logic.encodage_des_notes.shared_kernel.domain.model.encoder_notes_rapport import EncoderNotesRapport, \
    IdentiteEncoderNotesRapport
from infrastructure.encodage_de_notes.shared_kernel.repository.encoder_notes_rapport import \
    EncoderNotesRapportRepository


class EncoderNotesRapportRepositoryTest(TestCase):
    def setUp(self) -> None:
        self.rapport_repository = EncoderNotesRapportRepository()

        self.rapport = EncoderNotesRapport(
            entity_id=IdentiteEncoderNotesRapport(transaction_id=uuid.uuid4())
        )

    def test_should_save_rapport(self):
        self.rapport.add_note_enregistree(
            noma='1234567',
            numero_session=2,
            code_unite_enseignement='LDROI1200',
            annee_academique=2020,
        )

        self.rapport.add_note_non_enregistree(
            noma='1234567',
            numero_session=2,
            code_unite_enseignement='LDROI1200',
            annee_academique=2020,
            cause="Note invalide"
        )

        self.rapport_repository.save(self.rapport)

        rapport = self.rapport_repository.get(self.rapport.entity_id)
        self.assertEqual(len(rapport.get_notes_enregistrees()), 1)
        self.assertEqual(len(rapport.get_notes_non_enregistrees()), 1)
