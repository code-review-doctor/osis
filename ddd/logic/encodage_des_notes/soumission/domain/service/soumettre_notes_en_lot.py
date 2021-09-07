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
from typing import List, Dict

from ddd.logic.encodage_des_notes.soumission.builder.note_etudiant_identity_builder import NoteEtudiantIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.commands import SoumettreNotesCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.repository.i_note_etudiant import INoteEtudiantRepository
from osis_common.ddd import interface


class SoumettreNotesEnLot(interface.DomainService):

    @classmethod
    def soumettre(
            cls,
            cmd: 'SoumettreNotesCommand',
            note_etudiant_repo: 'INoteEtudiantRepository',
    ) -> List['IdentiteNoteEtudiant']:
        identite_builder = NoteEtudiantIdentityBuilder()
        identites = [identite_builder.build_from_command(cmd_note) for cmd_note in cmd.notes]

        notes = note_etudiant_repo.search(entity_ids=identites)
        notes_by_identite = {note.entity_id: note for note in notes}  # type: Dict[IdentiteNoteEtudiant, NoteEtudiant]

        notes_soumises = []
        for cmd_note in cmd.notes:
            identite = identite_builder.build_from_command(cmd_note)
            note_a_soumettre = notes_by_identite[identite]

            note_a_soumettre.soumettre()

            note_etudiant_repo.save(note_a_soumettre)

            notes_soumises.append(identite)

        return notes_soumises
