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
from ddd.logic.encodage_des_notes.soumission.builder.responsable_de_notes_identity_builder import \
    ResponsableDeNotesIdentityBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model._unite_enseignement_identite import \
    UniteEnseignementIdentiteBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.responsable_de_notes import ResponsableDeNotes
from ddd.logic.encodage_des_notes.soumission.dtos import ResponsableDeNotesFromRepositoryDTO
from osis_common.ddd import interface


class ResponsableDeNotesBuilder(interface.RootEntityBuilder):
    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'ResponsableDeNotes':
        pass

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'ResponsableDeNotesFromRepositoryDTO') -> 'ResponsableDeNotes':
        return ResponsableDeNotes(
            entity_id=ResponsableDeNotesIdentityBuilder().build_from_repository_dto(dto_object),
            unites_enseignements={
                UniteEnseignementIdentiteBuilder.build_from_repository_dto(dto_unite_enseignement_identite)
                for dto_unite_enseignement_identite in dto_object.unites_enseignements
            }
        )
