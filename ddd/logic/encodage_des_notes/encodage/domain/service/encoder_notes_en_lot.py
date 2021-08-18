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
from typing import List, Dict, Tuple

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from ddd.logic.encodage_des_notes.encodage.repository.note_etudiant import INoteEtudiantRepository
from osis_common.ddd import interface

NouvelleNote = str
EmailEtudiant = str


class EncoderNotesEnLot(interface.DomainService):

    @classmethod
    def execute(
            cls,
            notes_a_modifier: List['NoteEtudiant'],
            note_par_identite: Dict[IdentiteNoteEtudiant, Tuple[NouvelleNote, EmailEtudiant]],
            note_etudiant_repo: 'INoteEtudiantRepository'
    ) -> None:
        exceptions = []
        notes_a_persister = list()
        note_etudiant_par_identite = {n.entity_id: n for n in notes_a_modifier}
        for identite, t in note_par_identite.items():
            note_encodee, email_encode = t
            note_etudiant = note_etudiant_par_identite.get(identite)
            if note_etudiant:
                try:
                    note_etudiant.encoder(note_encodee, email_encode)
                    notes_a_persister.append(note_etudiant)
                except MultipleBusinessExceptions as e:
                    exceptions += list(e.exceptions)

        for note in notes_a_persister:
            note_etudiant_repo.save(note)

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)
