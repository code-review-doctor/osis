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
from ddd.logic.encodage_des_notes.soumission.builder.feuille_de_notes_identity_builder import \
    FeuilleDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model._note import NoteBuilder
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
            credits_unite_enseignement=dto_object.credits_unite_enseignement,
            notes={cls.__build_note_etudiant_from_repository_dto(note_dto) for note_dto in dto_object.notes}
        )

    @classmethod
    def __build_note_etudiant_from_repository_dto(cls, dto_object: 'NoteEtudiantFromRepositoryDTO') -> 'NoteEtudiant':
        return NoteEtudiant(
            entity_id=IdentiteNoteEtudiant(noma=dto_object.noma),
            email=dto_object.email,
            note=NoteBuilder.build(dto_object.note),
            date_limite_de_remise=dto_object.date_limite_de_remise,
            est_soumise=dto_object.est_soumise
        )
