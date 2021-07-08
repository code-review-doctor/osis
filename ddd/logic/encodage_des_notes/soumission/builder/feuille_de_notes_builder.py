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
from base.models.enums.exam_enrollment_justification_type import TutorJustificationTypes
from ddd.logic.encodage_des_notes.soumission.builder.feuille_de_notes_identity_builder import \
    FeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model._note import NoteManquante, Note, Justification, NoteChiffree
from ddd.logic.encodage_des_notes.soumission.domain.model._note_etudiant import NoteEtudiant, IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.soumission.domain.model.feuille_de_notes import FeuilleDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import FeuilleDeNotesFromRepositoryDTO, NoteEtudiantFromRepositoryDTO
from osis_common.ddd import interface


class FeuilleDeNotesBuilder(interface.RootEntityBuilder):
    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'FeuilleDeNotes':
        pass

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'FeuilleDeNotesFromRepositoryDTO') -> 'FeuilleDeNotes':
        return FeuilleDeNotes(
            entity_id=FeuilleDeNotesIdentityBuilder().build_from_repository_dto(dto_object),
            notes=[cls._build_note_etudiant_from_repository_dto(note_dto) for note_dto in dto_object.notes]
        )

    @classmethod
    def _build_note_etudiant_from_repository_dto(cls, dto_object: 'NoteEtudiantFromRepositoryDTO') -> 'NoteEtudiant':
        return NoteEtudiant(
            entity_id=IdentiteNoteEtudiant(noma=dto_object.noma),
            note=_build_note_from_value(dto_object.note),
            date_limite_de_remise=dto_object.date_limite_de_remise,
            est_soumise=dto_object.est_soumise
        )


def _build_note_from_value(note_value: str) -> 'Note':
    if _is_float(note_value):
        return NoteChiffree(float(note_value))
    if note_value:
        return Justification(TutorJustificationTypes[note_value])
    return NoteManquante()


def _is_float(value) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False
