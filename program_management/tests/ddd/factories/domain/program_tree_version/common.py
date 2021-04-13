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
from typing import Dict, Optional, List

import factory

from program_management.ddd import command
from program_management.ddd.domain.node import Node, NodeIdentity
from program_management.ddd.domain.prerequisite import PrerequisiteFactory
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.ddd.repositories import program_tree as program_tree_repository, \
    program_tree_version as program_tree_version_repository
from program_management.ddd.service.write import copy_program_version_service, copy_program_tree_service
from program_management.models.enums.node_type import NodeType
from program_management.tests.ddd.factories.authorized_relationship import AuthorizedRelationshipListFactory
from program_management.tests.ddd.factories.domain.prerequisite.prerequisite import PrerequisitesFactory
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory


class ProgramTreeVersionBuilder(factory.Factory):
    class Meta:
        model = ProgramTreeVersion
        abstract = False

    tree_data = None
    year = 2018
    start_year = 2018
    end_year = 2025

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> 'ProgramTreeVersion':
        return ProgramTreeVersionFactory(tree=build_tree(*args, **kwargs), persist=True)

    @classmethod
    def multiple(cls, n, *args, **kwargs) -> List['ProgramTreeVersion']:
        first_tree_version = cls(*args, **kwargs)

        result = [first_tree_version]
        for year in range(first_tree_version.entity_id.year, first_tree_version.entity_id.year + n - 1):
            identity = copy_program_version_service.copy_tree_version_to_next_year(
                command.CopyTreeVersionToNextYearCommand(
                    from_year=year,
                    from_offer_acronym=first_tree_version.entity_id.offer_acronym,
                    from_offer_code=first_tree_version.program_tree_identity.code,
                    from_version_name=first_tree_version.version_name,
                    from_transition_name=first_tree_version.transition_name
                )
            )
            result.append(program_tree_version_repository.ProgramTreeVersionRepository.get(identity))

        for from_tree_version, to_tree_version in zip(result, result[1:]):
            identity = copy_program_tree_service.copy_program_tree_to_next_year(
                command.CopyProgramTreeToNextYearCommand(
                    code=from_tree_version.program_tree_identity.code,
                    year=from_tree_version.program_tree_identity.year
                )
            )
            to_tree_version.tree = program_tree_repository.ProgramTreeRepository.get(identity)

        return result


def build_tree(
        tree_data: Dict,
        year: int,
        start_year: int,
        end_year: Optional[int],
) -> 'ProgramTree':
    root_node = build_node(tree_data, year, start_year, end_year, {})
    authorized_relationships = AuthorizedRelationshipListFactory.load_from_fixture()
    tree = ProgramTreeFactory(root_node=root_node, authorized_relationships=authorized_relationships, persist=True)
    tree.prerequisites = build_prerequisites(tree, tree_data.get("prerequisites", []))
    return tree


def build_prerequisites(tree: 'ProgramTree', prerequisites_data: List):
    prerequisites = [
        PrerequisiteFactory().from_expression(
            prerequisite_expression, NodeIdentity(code, tree.root_node.year),
            tree.entity_id
        ) for code, prerequisite_expression in prerequisites_data
    ]
    return PrerequisitesFactory(context_tree=tree.entity_id, prerequisites=prerequisites)


def build_node(
        node_data: Dict,
        year: int,
        start_year: int,
        end_year: Optional[int],
        nodes_generated: Dict,
) -> 'Node':
    if node_data["code"] in nodes_generated:
        return nodes_generated[node_data["code"]]

    node_factory = get_node_factory(node_data["node_type"])
    node = node_factory(
        code=node_data["code"],
        title=node_data["title"],
        start_year=start_year,
        end_date=end_year,
        year=year,
        node_type=node_data["node_type"],
        persist=True
    )
    nodes_generated[node.code] = node

    children_node = [
        build_node(child_data, year, start_year, end_year, nodes_generated)
        for child_data in node_data.get("children", [])
    ]
    children_link = [
        LinkFactory(parent=node, child=child_node, order=order)
        for child_node, order in zip(children_node, itertools.count())
    ]
    return node


def get_node_factory(node_type: str):
    return NodeLearningUnitYearFactory if node_type == NodeType.LEARNING_UNIT else NodeGroupYearFactory
