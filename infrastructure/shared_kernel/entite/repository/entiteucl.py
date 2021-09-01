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
from typing import List, Optional

from base.models.entity_version import EntityVersion
from ddd.logic.shared_kernel.entite.builder.entite_builder import EntiteBuilder
from ddd.logic.shared_kernel.entite.domain.model.entiteucl import EntiteUCL, IdentiteUCLEntite
from ddd.logic.shared_kernel.entite.dtos import EntiteRepositoryDTO
from ddd.logic.shared_kernel.entite.repository.entiteucl import IEntiteUCLRepository
from osis_common.ddd.interface import ApplicationService


class EntiteUCLRepository(IEntiteUCLRepository):
    @classmethod
    def search(cls, entity_ids: Optional[List['IdentiteUCLEntite']] = None, **kwargs) -> List['EntiteUCL']:
        pass

    @classmethod
    def search_with_parents(cls, entity_ids: Optional[List['IdentiteUCLEntite']] = None, **kwargs) -> List['EntiteUCL']:
        if not entity_ids:
            return []
        acronyms = [entity_id.sigle for entity_id in entity_ids]
        cte = EntityVersion.objects.with_children(
            'acronym',
            'entity_type',
            'title',
            'entity__location',
            'entity__postal_code',
            'entity__city',
            'entity__country',
            'entity__phone',
            'entity__fax',
            acronym__in=acronyms
        )
        qs = cte.queryset().with_cte(cte).distinct('acronym').order_by('acronym')

        rows_by_entity_id = {row['entity_id']: row for row in qs}
        builder = EntiteBuilder()
        dtos = [cls._convert_row_to_repository_dto(row, rows_by_entity_id) for row in qs]
        return [builder.build_from_repository_dto(dto) for dto in dtos]

    @classmethod
    def _convert_row_to_repository_dto(cls, row, rows_by_entity_id) -> 'EntiteRepositoryDTO':
        parent = rows_by_entity_id.get(row['parent_id'])
        return EntiteRepositoryDTO(
            sigle=row['acronym'],
            parent_sigle=parent['acronym'] if parent else "",
            type=row['entity_type'],
            intitule=row['title'],
            rue_numero=row['entity__location'],
            code_postal=row['entity__postal_code'],
            ville=row['entity__city'],
            pays=row['entity__country'],
            telephone=row['entity__phone'],
            fax=row['entity__fax'],
        )

    @classmethod
    def delete(cls, entity_id: 'IdentiteUCLEntite', **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def save(cls, entity: 'EntiteUCL') -> None:
        pass

    @classmethod
    def get_all_identities(cls) -> List['IdentiteUCLEntite']:
        pass

    @classmethod
    def get(cls, entity_id: 'IdentiteUCLEntite') -> 'EntiteUCL':
        entites = cls.search_with_parents([entity_id])
        return next(entite for entite in entites if entite.entity_id == entity_id)
