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
import abc
from typing import List, Optional, Set

from base.models.enums.exam_enrollment_justification_type import JustificationTypes
from ddd.logic.encodage_des_notes.encodage.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from osis_common.ddd import interface
from osis_common.ddd.interface import ApplicationService


class INoteEtudiantRepository(interface.AbstractRepository):

    @classmethod
    @abc.abstractmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteNoteEtudiant']] = None,
            noms_cohortes: List[str] = None,
            annee_academique: int = None,
            numero_session: int = None,
            nomas: List[str] = None,
            note_manquante: bool = False,
            justification: JustificationTypes = None,
            **kwargs
    ) -> List['NoteEtudiant']:
        pass

    @classmethod
    @abc.abstractmethod
    def search_notes_identites(
            cls,
            noms_cohortes: List[str] = None,
            annee_academique: int = None,
            numero_session: int = None,
            nomas: List[str] = None,
            note_manquante: bool = False,
            **kwargs
    ) -> Set['IdentiteNoteEtudiant']:
        pass

    @classmethod
    @abc.abstractmethod
    def delete(cls, entity_id: 'IdentiteNoteEtudiant', **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def save(cls, entity: 'NoteEtudiant') -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def get_all_identities(cls) -> List['IdentiteNoteEtudiant']:
        pass

    @classmethod
    @abc.abstractmethod
    def get(cls, entity_id: 'IdentiteNoteEtudiant') -> 'NoteEtudiant':
        pass
