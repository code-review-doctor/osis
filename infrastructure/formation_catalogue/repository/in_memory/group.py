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
import itertools
from typing import List, Optional

from education_group.ddd.domain import exception
from education_group.ddd.repository import group as group_repository


class InMemoryGroupRepository(group_repository.GroupRepository):
    _groups = list()  # type: List['Group']

    @classmethod
    def search_groups_last_occurence(cls, from_year: int) -> List['Group']:
        datas = (root_entity for root_entity in cls._groups if root_entity.entity_id.year >= from_year)
        group_by_code = itertools.groupby(datas, lambda group: group.code)
        return [max(groups, key=lambda group: group.year) for acronym, groups in group_by_code]

    @classmethod
    def create(cls, group: 'Group', **_) -> 'GroupIdentity':
        cls._groups.append(group)
        from program_management.tests.ddd.factories import node as node_factory
        node_factory.NodeGroupYearFactory.from_group(group, persist=True)
        return group.entity_id

    @classmethod
    def update(cls, group: 'Group', **_) -> 'GroupIdentity':
        if group not in cls._groups:
            raise exception.GroupNotFoundException()
        return group.entity_id

    @classmethod
    def get(cls, entity_id: 'GroupIdentity') -> 'Group':
        result = next((group for group in cls._groups if group.entity_id == entity_id), None)
        if not result:
            raise exception.GroupNotFoundException()
        return result

    @classmethod
    def search(cls, entity_ids: Optional[List['GroupIdentity']] = None, code=None, **kwargs) -> List['Group']:
        if entity_ids:
            return [group for group in cls._groups if group.entity_id in entity_ids]
        if code:
            return [group for group in cls._groups if group.entity_id.code == code]
        return []

    @classmethod
    def delete(cls, entity_id: 'GroupIdentity', **_) -> None:
        group_to_delete = next((group for group in cls._groups if group.entity_id == entity_id), None)
        if group_to_delete:
            cls._groups.remove(group_to_delete)
