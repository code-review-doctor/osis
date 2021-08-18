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
from typing import List, Optional

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.encodage_des_notes.shared_kernel.dtos import EnseignantDTO
from ddd.logic.encodage_des_notes.soumission.domain.model._unite_enseignement_identite import \
    UniteEnseignementIdentiteBuilder
from ddd.logic.encodage_des_notes.soumission.domain.model.responsable_de_notes import IdentiteResponsableDeNotes
from ddd.logic.encodage_des_notes.soumission.domain.model.responsable_de_notes import ResponsableDeNotes
from ddd.logic.encodage_des_notes.soumission.repository.i_responsable_de_notes import IResponsableDeNotesRepository


class ResponsableDeNotesInMemoryRepository(InMemoryGenericRepository, IResponsableDeNotesRepository):
    entities = list()  # type: List[ResponsableDeNotes]

    @classmethod
    def get_detail_enseignant(cls, entity_id: 'IdentiteResponsableDeNotes') -> 'EnseignantDTO':
        return EnseignantDTO(nom='Chileng', prenom='Jean-Michel')

    @classmethod
    def get_for_unite_enseignement(cls, code_unite_enseignement: 'str', annee_academique: int) -> 'ResponsableDeNotes':
        ue_identite = UniteEnseignementIdentiteBuilder.build_from_code_and_annee(
            code_unite_enseignement,
            annee_academique
        )
        return next(
            (entity for entity in cls.entities if ue_identite in entity.unites_enseignements),
            None
        )

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['IdentiteResponsableDeNotes']] = None,
            codes_unites_enseignement: List[str] = None,
            annee_academique: Optional[int] = None,
            **kwargs
    ) -> List['ResponsableDeNotes']:
        return list(
            filter(
                lambda entity: _filter(entity, codes_unites_enseignement, annee_academique),
                cls.entities
            )
        )


def _filter(entity, codes_unites_enseignement, annee_academique):
    matches = set()
    if codes_unites_enseignement:
        matches.add(
            any(
                entity.is_responsable_unite_enseignement(code, annee_academique)
                for code in codes_unites_enseignement
            )
        )
    return all(matches)
