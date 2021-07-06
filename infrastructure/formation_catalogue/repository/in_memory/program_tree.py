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
from typing import Optional, List

from osis_common.ddd import interface
from program_management.ddd import command
from program_management.ddd.domain import exception, program_tree
from program_management.ddd.repositories import program_tree as tree_repository


class InMemoryProgramTreeRepository(tree_repository.ProgramTreeRepository):
    _trees = list()  # type: List[ProgramTree]

    @classmethod
    def create(
            cls,
            program_tree: 'ProgramTree',
            create_orphan_group_service: interface.ApplicationService = None,
            copy_group_service: interface.ApplicationService = None,
    ) -> 'ProgramTreeIdentity':
        cls._trees.append(program_tree)
        return program_tree.entity_id

    @classmethod
    def update(cls, program_tree: 'ProgramTree', **_) -> 'ProgramTreeIdentity':
        if program_tree not in cls._trees:
            raise exception.ProgramTreeNotFoundException()
        return program_tree.entity_id

    @classmethod
    def get(cls, entity_id: 'ProgramTreeIdentity') -> 'ProgramTree':
        result = next((tree for tree in cls._trees if tree.entity_id == entity_id), None)
        if not result:
            raise exception.ProgramTreeNotFoundException()
        return result

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['ProgramTreeIdentity']] = None,
            root_ids: List[int] = None,
            code: str = None
    ) -> List['ProgramTree']:
        result = []
        if entity_ids:
            return [root_entity for root_entity in cls._trees if root_entity.entity_id in entity_ids]
        if code:
            return [root_entity for root_entity in cls._trees if root_entity.entity_id.code == code]
        return result

    @classmethod
    def search_from_children(cls, node_ids: List['NodeIdentity'], **kwargs) -> List['ProgramTree']:
        result = []
        set_node_ids = set(node_ids)
        for tree in cls._trees:
            children_nodes = tree.get_all_nodes() - {tree.root_node}
            children_nodes_ids = set([node.entity_id for node in children_nodes])
            if not children_nodes_ids.isdisjoint(set_node_ids):
                result.append(tree)
        return result

    @classmethod
    def search_last_occurence(cls, from_year: int) -> List['ProgramTree']:
        datas = (root_entity for root_entity in cls._trees if root_entity.entity_id.year >= from_year)
        group_by_code = itertools.groupby(datas, lambda tree: tree.entity_id.code)
        return [max(tree, key=lambda tree: tree.entity_id.year) for code, tree in group_by_code]

    @classmethod
    def get_all_identities(cls) -> List['ProgramTreeIdentity']:
        result = set()
        for tree in cls._trees:
            identities = {program_tree.ProgramTreeIdentity(node.code, node.year) for node in tree.get_all_nodes()
                          if not node.is_learning_unit()}
            result.union(identities)
        return list(result)

    @classmethod
    def delete(
            cls,
            entity_id: 'ProgramTreeIdentity',
            delete_node_service: interface.ApplicationService = None,
    ) -> None:
        program_tree = cls.get(entity_id)
        nodes = program_tree.get_all_nodes()

        idx = -1
        for idx, entity in enumerate(cls._trees):
            if entity.entity_id == entity_id:
                break
        if idx >= 0:
            cls._trees.pop(idx)

        for node in nodes:
            cmd = command.DeleteNodeCommand(code=node.code, year=node.year, node_type=node.node_type.name,
                                            acronym=node.title)
            delete_node_service(cmd)