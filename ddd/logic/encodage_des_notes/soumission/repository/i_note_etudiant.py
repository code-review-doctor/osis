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
from typing import List, Optional, Tuple, Set

from ddd.logic.encodage_des_notes.soumission.domain.model.note_etudiant import IdentiteNoteEtudiant, NoteEtudiant
from ddd.logic.encodage_des_notes.soumission.dtos import DateEcheanceNoteDTO
from osis_common.ddd import interface
from osis_common.ddd.interface import ApplicationService


SearchCriteria = Tuple[str, int, int]


class INoteEtudiantRepository(interface.AbstractRepository):

    @classmethod
    @abc.abstractmethod
    def search(cls, entity_ids: Optional[List['IdentiteNoteEtudiant']] = None, **kwargs) -> List['NoteEtudiant']:
        pass

    @classmethod
    @abc.abstractmethod
    def search_by_code_unite_enseignement_annee_session(
            cls,
            criterias: List[SearchCriteria]
    ) -> List['NoteEtudiant']:
        pass

    @classmethod
    @abc.abstractmethod
    def search_dates_echeances(
            cls,
            notes_identites: Set[IdentiteNoteEtudiant]
    ) -> List[DateEcheanceNoteDTO]:
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
