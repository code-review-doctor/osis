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

from education_group.ddd.command import CopyGroupCommand
from education_group.ddd.service.write import copy_group_service
from osis_common.ddd import interface
from program_management.ddd.business_types import *
from program_management.ddd.domain import node, program_tree
from program_management.ddd.domain.exception import ProgramTreeNotFoundException
from program_management.ddd.repositories import program_tree as program_tree_repository, node as node_repository


class GetOrCreateNode(interface.DomainService):
    @classmethod
    def for_group_year_node(cls, to_year: int, base_node: 'NodeGroupYear') -> 'Node':
        repo = program_tree_repository.ProgramTreeRepository()

        tree_identity = program_tree.ProgramTreeIdentity(code=base_node.code, year=to_year)

        try:
            return repo.get(tree_identity).root_node
        except ProgramTreeNotFoundException:
            cls._create_group(base_node)
            return repo.get(tree_identity).root_node

    @classmethod
    def for_learning_unit_node(cls, to_year: int, base_node: 'NodeLearningUnitYear') -> 'Node':
        repo = node_repository.NodeRepository()

        node_identity = node.NodeIdentity(code=base_node.code, year=to_year)

        return repo.get(node_identity)

    @classmethod
    def _create_group(cls, n: 'NodeGroupYear'):
        copy_group_service.copy_group(
            CopyGroupCommand(
                from_year=n.year,
                from_code=n.code
            )
        )
