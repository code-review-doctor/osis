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
from ddd.logic.encodage_des_notes.encodage.builder.identite_note_etudiant_builder import NoteEtudiantIdentityBuilder
from ddd.logic.encodage_des_notes.encodage.domain.model._note import NoteBuilder
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import NoteEtudiant
from ddd.logic.encodage_des_notes.encodage.domain.validator.validators_by_business_action import \
    EncoderNotesValidatorList
from ddd.logic.encodage_des_notes.encodage.dtos import NoteEtudiantFromRepositoryDTO

from osis_common.ddd import interface
from osis_common.ddd.interface import CommandRequest


class NoteEtudiantBuilder(interface.RootEntityBuilder):
    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'NoteEtudiant':
        raise NotImplementedError

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'NoteEtudiantFromRepositoryDTO') -> 'NoteEtudiant':
        return NoteEtudiant(
            entity_id=NoteEtudiantIdentityBuilder().build_from_repository_dto(dto_object),
            email=dto_object.email,
            note=NoteBuilder.build(dto_object.note),
            echeance_gestionnaire=dto_object.echeance_gestionnaire,
            nom_cohorte=dto_object.nom_cohorte,
            note_decimale_autorisee=dto_object.note_decimale_autorisee
        )

    @classmethod
    def build_from_ancienne_note(
            cls,
            ancienne_note: 'NoteEtudiant',
            nouvelle_note: str,
            email_encode: str
    ) -> 'NoteEtudiant':
        EncoderNotesValidatorList(
            note_etudiant=ancienne_note,
            email=email_encode,
            note=nouvelle_note,
        ).validate()
        return NoteEtudiant(
            entity_id=ancienne_note.entity_id,
            email=ancienne_note.email,
            note=NoteBuilder.build(nouvelle_note),
            echeance_gestionnaire=ancienne_note.echeance_gestionnaire,
            nom_cohorte=ancienne_note.nom_cohorte,
            note_decimale_autorisee=ancienne_note.note_decimale_autorisee,
        )

