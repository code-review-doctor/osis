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
from typing import List, Dict

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.soumission.builder.note_etudiant_identity_builder import NoteEtudiantIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.commands import EncoderNotesEtudiantCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import \
    EncoderNotesEtudiantEnLotLigneBusinessExceptions
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from osis_common.ddd import interface


class EncoderNotesEtudiantEnLot(interface.DomainService):

    @classmethod
    def execute(
            cls,
            cmd: 'EncoderNotesEtudiantCommand',
            note_etudiant_repo: 'INoteEtudiantRepository',
    ) -> List['IdentiteNoteEtudiant']:
        identite_builder = NoteEtudiantIdentityBuilder()
        identites_notes_a_encoder = [
            identite_builder.build_from_encoder_note_command(cmd, cmd_note)
            for cmd_note in cmd.notes
        ]

        notes_a_encoder = note_etudiant_repo.search(entity_ids=identites_notes_a_encoder)
        notes_par_identite = {n.entity_id: n for n in notes_a_encoder}  # type: Dict[IdentiteNoteEtudiant, NoteEtudiant]

        exceptions = []
        notes_a_persister = []

        for note_encodee_cmd in cmd.notes:
            identite = identite_builder.build_from_encoder_note_command(cmd, note_encodee_cmd)

            note_a_modifier = notes_par_identite.get(identite)

            if note_a_modifier:
                try:
                    note_a_modifier.encoder(note_encodee_cmd.email_etudiant, note_encodee_cmd.note)
                    notes_a_persister.append(note_a_modifier)
                except MultipleBusinessExceptions as e:
                    exceptions += [
                        EncoderNotesEtudiantEnLotLigneBusinessExceptions(note_id=identite, exception=business_exception)
                        for business_exception in e.exceptions
                    ]

        for note in notes_a_persister:
            note_etudiant_repo.save(note)

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)

        return [n.entity_id for n in notes_a_persister]
