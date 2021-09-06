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
from typing import List, Optional, Dict

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.shared_kernel.entite.domain.model.entiteucl import EntiteUCL, IdentiteUCLEntite
from ddd.logic.shared_kernel.entite.repository.entiteucl import IEntiteUCLRepository


class EntiteUCLInMemoryRepository(InMemoryGenericRepository, IEntiteUCLRepository):
    entities = list()  # type: List[EntiteUCL]

    @classmethod
    def search_with_parents(cls, entity_ids: Optional[List['IdentiteUCLEntite']] = None, **kwargs) -> List['EntiteUCL']:
        entites = cls.search(entity_ids)
        result = entites.copy()
        for entite in entites:
            result.extend(cls._get_hierarchy(entite))
        return result

    @classmethod
    def _get_hierarchy(cls, entite: 'EntiteUCL', dict_sigle_entite: Dict[str, 'EntiteUCL'] = None) -> List['EntiteUCL']:
        if not dict_sigle_entite:
            dict_sigle_entite = {entity.sigle: entity for entity in cls.entities}

        parent_entite = cls._get_parent(entite, dict_sigle_entite)
        if parent_entite:
            return [parent_entite] + cls._get_hierarchy(parent_entite, dict_sigle_entite)
        return []

    @classmethod
    def _get_parent(cls, entite: 'EntiteUCL', dict_sigle_entite: Dict[str, 'EntiteUCL']) -> Optional['EntiteUCL']:
        if entite.parent:
            return dict_sigle_entite.get(entite.parent.sigle)
        return None
