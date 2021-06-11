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
from program_management.ddd.domain import exception
from program_management.ddd.repositories import program_tree_version as tree_version_repository


class InMemoryProgramTreeVersionRepository(tree_version_repository.ProgramTreeVersionRepository):
    _trees_version = list()  # type: List[ProgramTreeVersion]

    @classmethod
    def create(
            cls,
            program_tree_version: 'ProgramTreeVersion',
            **_
    ) -> 'ProgramTreeVersionIdentity':
        cls._trees_version.append(program_tree_version)
        return program_tree_version.entity_id

    @classmethod
    def update(cls, program_tree_version: 'ProgramTreeVersion', **_) -> 'ProgramTreeVersionIdentity':
        if program_tree_version not in cls._trees_version:
            raise exception.ProgramTreeVersionNotFoundException()
        return program_tree_version.entity_id

    @classmethod
    def get(cls, entity_id: 'ProgramTreeVersionIdentity') -> 'ProgramTreeVersion':
        result = next((tree for tree in cls._trees_version if tree.entity_id == entity_id), None)
        if not result:
            raise exception.ProgramTreeVersionNotFoundException()
        return result

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['ProgramTreeVersionIdentity']] = None,
            version_name: str = None,
            offer_acronym: str = None,
            transition_name: str = None,
            code: str = None,
            year: int = None,
            **kwargs
    ) -> List['ProgramTreeVersion']:
        result = cls._trees_version  # type: List[ProgramTreeVersion]
        if entity_ids:
            result = (tree_version for tree_version in result if tree_version.entity_id in entity_ids)
        if version_name is not None:
            result = (tree_version for tree_version in result if tree_version.version_name == version_name)
        if offer_acronym is not None:
            result = (tree_version for tree_version in result if tree_version.entity_id.offer_acronym == offer_acronym)
        if transition_name is not None:
            result = (tree_version for tree_version in result if tree_version.transition_name == transition_name)
        if year:
            result = (tree_version for tree_version in result if tree_version.entity_id.year == year)
        return list(result)

    @classmethod
    def search_versions_from_trees(cls, trees: List['ProgramTree']) -> List['ProgramTreeVersion']:
        tree_entities = {tree.entity_id for tree in trees}
        return [tree_version for tree_version in cls._trees_version if tree_version.tree.entity_id in tree_entities]

    @classmethod
    def search_last_occurence(cls, from_year: int) -> List['ProgramTreeVersion']:
        datas = (root_entity for root_entity in cls._trees_version if root_entity.entity_id.year >= from_year)
        group_by_acronym = itertools.groupby(datas, lambda tree: tree.entity_id.offer_acronym)
        return [max(tree, key=lambda tree: tree.entity_id.year) for code, tree in group_by_acronym]

    @classmethod
    def delete(
           cls,
           entity_id: 'ProgramTreeVersionIdentity',
           delete_program_tree_service: interface.ApplicationService = None
    ) -> None:
        tree_version = cls.get(entity_id)

        idx = -1
        for idx, entity in enumerate(cls._trees_version):
            if entity.entity_id == entity_id:
                break
        if idx >= 0:
            cls._trees_version.pop(idx)

        cmd = command.DeleteProgramTreeCommand(
            code=tree_version.tree.entity_id.code,
            year=tree_version.tree.entity_id.year
        )
        delete_program_tree_service(cmd)