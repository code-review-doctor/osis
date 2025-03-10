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
from ddd.logic.encodage_des_notes.encodage.commands import EncoderNoteCommand
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant
from ddd.logic.encodage_des_notes.encodage.dtos import NoteEtudiantFromRepositoryDTO
from osis_common.ddd.interface import EntityIdentityBuilder


class NoteEtudiantIdentityBuilder(EntityIdentityBuilder):
    @classmethod
    def build_from_command(cls, cmd: 'EncoderNoteCommand') -> 'IdentiteNoteEtudiant':
        raise NotImplementedError

    @classmethod
    def build_from_repository_dto(
            cls,
            dto_object: 'NoteEtudiantFromRepositoryDTO'
    ) -> 'IdentiteNoteEtudiant':
        return IdentiteNoteEtudiant(
            noma=dto_object.noma,
            code_unite_enseignement=dto_object.code_unite_enseignement,
            annee_academique=dto_object.annee_academique,
            numero_session=dto_object.numero_session,
        )

    @classmethod
    def build(
            cls,
            noma: str,
            code_unite_enseignement: str,
            annee: int,
            numero_session: int
    ) -> 'IdentiteNoteEtudiant':
        return IdentiteNoteEtudiant(
            noma=noma,
            code_unite_enseignement=code_unite_enseignement,
            annee_academique=annee,
            numero_session=numero_session,
        )
