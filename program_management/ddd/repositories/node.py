##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import Optional, List

from django.db.models import Q

from osis_common.ddd import interface
from osis_common.ddd.interface import RootEntity
from program_management.ddd.business_types import *
from program_management.ddd.repositories import load_node
from program_management.models.element import Element


# TODO:: Add tests
class NodeRepository(interface.AbstractRepository):

    @classmethod
    def save(cls, entity: RootEntity) -> None:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: 'NodeIdentity', **_) -> None:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'NodeIdentity') -> Optional['Node']:
        search_result = cls.search(entity_ids=[entity_id])
        if search_result:
            return search_result[0]

    @classmethod
    def get_next_learning_unit_year_node(cls, entity_id: 'NodeIdentity') -> Optional['Node']:
        qs = Element.objects.filter(
            learning_unit_year__academic_year__year=entity_id.year+1,
            learning_unit_year__learning_unit__learningunityear__acronym=entity_id.code
        )
        nodes = load_node.load_multiple(qs.values_list('pk', flat=True))
        return nodes[0] if nodes else None

    @classmethod
    def search(cls, entity_ids: Optional[List['NodeIdentity']] = None, year: int = None, **kwargs) -> List['Node']:
        if entity_ids:
            return _search_by_entity_ids(entity_ids)
        if year:
            return _search_by_year(year)
        return []


def _search_by_year(year: int) -> List['Node']:
    qs_group = Element.objects.filter(group_year__academic_year__year=year)
    qs_learning_unit = Element.objects.filter(learning_unit_year__academic_year__year=year)
    qs = qs_group.union(qs_learning_unit)

    return load_node.load_multiple(qs.values_list('pk', flat=True))


def _search_by_entity_ids(entity_ids: List['NodeIdentity']) -> List['Node']:

    filter_search_from_group_year = _build_group_year_where_clause(entity_ids[0])
    for identity in entity_ids[1:]:
        filter_search_from_group_year |= _build_group_year_where_clause(identity)
    qs = Element.objects.all().filter(filter_search_from_group_year)

    filter_search_from_learning_unit = _build_learning_unit_year_where_clause(entity_ids[0])
    for identity in entity_ids[1:]:
        filter_search_from_learning_unit |= _build_learning_unit_year_where_clause(identity)
    qs_bis = Element.objects.all().filter(filter_search_from_learning_unit)

    qs = qs.union(qs_bis)

    return load_node.load_multiple(qs.values_list('pk', flat=True))


def _build_group_year_where_clause(node_identity: 'NodeIdentity') -> Q:
    return Q(
        group_year__partial_acronym=node_identity.code,
        group_year__academic_year__year=node_identity.year
    )


def _build_learning_unit_year_where_clause(node_identity: 'NodeIdentity') -> Q:
    return Q(
        learning_unit_year__acronym=node_identity.code,
        learning_unit_year__academic_year__year=node_identity.year
    )
