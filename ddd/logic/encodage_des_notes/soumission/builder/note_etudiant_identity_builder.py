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
from typing import Union

from ddd.logic.encodage_des_notes.soumission.commands import EncoderNoteCommand, SoumettreNoteCommand, \
    EncoderNotesEtudiantCommand
from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.soumission.dtos import NoteEtudiantFromRepositoryDTO
from osis_common.ddd.interface import EntityIdentityBuilder


class NoteEtudiantIdentityBuilder(EntityIdentityBuilder):
    @classmethod
    def build_from_command(
            cls,
            cmd: Union['EncoderNoteCommand', 'SoumettreNoteCommand']
    ) -> 'IdentiteNoteEtudiant':
        return IdentiteNoteEtudiant(
            numero_session=cmd.numero_session,
            code_unite_enseignement=cmd.code_unite_enseignement,
            annee_academique=cmd.annee_unite_enseignement,
            noma=cmd.noma_etudiant
        )

    @classmethod
    def build_from_encoder_note_command(
            cls,
            cmd: 'EncoderNotesEtudiantCommand',
            cmd_note: 'EncoderNoteCommand'
    ) -> 'IdentiteNoteEtudiant':
        return IdentiteNoteEtudiant(
            numero_session=cmd.numero_session,
            code_unite_enseignement=cmd.code_unite_enseignement,
            annee_academique=cmd.annee_unite_enseignement,
            noma=cmd_note.noma_etudiant
        )

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'NoteEtudiantFromRepositoryDTO') -> 'IdentiteNoteEtudiant':
        return IdentiteNoteEtudiant(
            numero_session=dto_object.numero_session,
            code_unite_enseignement=dto_object.code_unite_enseignement,
            annee_academique=dto_object.annee_academique,
            noma=dto_object.noma
        )
