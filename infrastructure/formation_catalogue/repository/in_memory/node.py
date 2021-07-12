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
from typing import Optional, List

from program_management.ddd.domain import exception
from program_management.ddd.repositories import node as node_repository


class InMemoryNodeRepository(node_repository.NodeRepository):
    _nodes = list()  # type: List[Node]

    @classmethod
    def create(cls, node: 'Node', **_) -> 'NodeIdentity':
        cls._nodes.append(node)
        return node.entity_id

    @classmethod
    def update(cls, node: 'Node', **_) -> 'NodeIdentity':
        if node not in cls._nodes:
            raise exception.NodeNotFoundException()
        return node.entity_id

    @classmethod
    def get(cls, node_id: 'NodeIdentity') -> Optional['Node']:
        result = next((node for node in cls._nodes if node.entity_id == node_id), None)
        if not result:
            raise exception.NodeNotFoundException()
        return result

    @classmethod
    def search(cls, entity_ids: List['NodeIdentity'] = None, year: int = None, **kwargs) -> List['Node']:
        if entity_ids:
            return [node for node in cls._nodes if node.entity_id in entity_ids]
        if year:
            return [node for node in cls._nodes if node.entity_id.year == year]
        return []

    @classmethod
    def delete(cls, node_id: 'NodeIdentity', **_) -> None:
        node_to_delete = next((node for node in cls._nodes if node.entity_id == node_id), None)
        if node_to_delete:
            cls._nodes.remove(node_to_delete)