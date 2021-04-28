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

from base.models.enums.education_group_types import TrainingType, MiniTrainingType
from education_group.tests.ddd.factories.group import GroupFactory
from education_group.tests.ddd.factories.training import TrainingFactory
from education_group.tests.factories.mini_training import MiniTrainingFactory
from education_group.ddd.repository import training as training_repository, mini_training as mini_trainig_repository, \
    group as group_repository
from program_management.ddd import command
from program_management.ddd.command import CreateProgramTreeSpecificVersionCommand, \
    CreateProgramTreeTransitionVersionCommand
from program_management.ddd.domain.node import Node, NodeIdentity, NodeLearningUnitYear, NodeGroupYear
from program_management.ddd.domain.prerequisite import PrerequisiteFactory
from program_management.ddd.domain.program_tree import ProgramTree, ProgramTreeIdentity
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion, NOT_A_TRANSITION, STANDARD
from program_management.ddd.repositories import program_tree as program_tree_repository, \
    program_tree_version as program_tree_version_repository, node as node_repository
from program_management.ddd.service.write import copy_program_version_service, copy_program_tree_service, \
    create_and_postpone_tree_specific_version_service, create_and_postpone_tree_transition_version_service
from program_management.models.enums.node_type import NodeType
from program_management.tests.ddd.factories.authorized_relationship import AuthorizedRelationshipListFactory
from program_management.tests.ddd.factories.domain.prerequisite.prerequisite import PrerequisitesFactory
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory


# TODO simplify creation of transition and specific version
class ProgramTreeVersionBuilder:
    tree_data = None
    year = 2018
    start_year = 2018
    end_year = 2025

    def __new__(cls, *args, **kwargs) -> List['ProgramTreeVersion']:
        tree_data = kwargs.get("tree_data", cls.tree_data)
        year = kwargs.get("year", cls.year)
        start_year = kwargs.get("start_year", cls.start_year)
        end_year = kwargs.get("end_year", cls.end_year)

        initial_tree_version = build_tree_version(tree_data, year, start_year, end_year)
        sub_tree_versions = build_sub_trees(initial_tree_version)
        tree_versions = cls._postpone_tree_versions(initial_tree_version)
        for tree_version in [initial_tree_version] + sub_tree_versions:
            cls._postpone_program_tree(tree_version)
        other_tree_version = itertools.chain.from_iterable(
            [cls._postpone_tree_versions(tree_version) for tree_version in sub_tree_versions]
        )
        all_tree_version = tree_versions + list(other_tree_version)

        cls.__persist_nodes(all_tree_version)
        trainings = cls.__create_trainings(all_tree_version)
        cls.__persist_trainings(trainings)
        mini_trainings = cls.__create_mini_trainings(all_tree_version)
        cls.__persist_mini_trainings(mini_trainings)
        groups = cls.__create_groups(all_tree_version)
        cls.__persist_groups(groups)

        return tree_versions

    @classmethod
    def _postpone_tree_versions(cls, initial_tree_version: 'ProgramTreeVersion') -> List['ProgramTreeVersion']:
        identities = [
            copy_program_version_service.copy_tree_version_to_next_year(
                command.CopyTreeVersionToNextYearCommand(
                    from_year=year,
                    from_offer_acronym=initial_tree_version.entity_id.offer_acronym,
                    from_offer_code=initial_tree_version.program_tree_identity.code,
                    from_version_name=initial_tree_version.version_name,
                    from_transition_name=initial_tree_version.transition_name
                )
            )
            for year in range(initial_tree_version.entity_id.year, initial_tree_version.end_year.year)
        ]
        return [initial_tree_version] + [
            program_tree_version_repository.ProgramTreeVersionRepository.get(identity) for identity in identities
        ]

    @classmethod
    def _postpone_program_tree(cls, initial_tree_version: 'ProgramTreeVersion') -> List['ProgramTreeIdentity']:
        for year in range(initial_tree_version.entity_id.year, initial_tree_version.end_year.year):
            copy_program_tree_service.copy_program_tree_to_next_year(
                command.CopyProgramTreeToNextYearCommand(
                    code=initial_tree_version.program_tree_identity.code,
                    year=year
                )
            )

    @classmethod
    def __persist_nodes(cls, tree_versions: List['ProgramTreeVersion']) -> List['NodeIdentity']:
        nodes = itertools.chain.from_iterable(tree_version.get_tree().get_all_nodes() for tree_version in tree_versions)
        repo = node_repository.NodeRepository()
        return [repo.create(node) for node in nodes]

    @classmethod
    def __create_trainings(cls, tree_versions: List['ProgramTreeVersion']) -> List['Training']:
        training_nodes = itertools.chain.from_iterable(
            tree_version.get_tree().get_all_nodes(types=set(TrainingType.all())) for tree_version in tree_versions
        )
        return [TrainingFactory.from_node(node) for node in training_nodes]

    @classmethod
    def __persist_trainings(cls, trainings: List['Training']):
        repo = training_repository.TrainingRepository()
        return [repo.create(training) for training in trainings]

    @classmethod
    def __create_mini_trainings(cls, tree_versions: List['ProgramTreeVersion']) -> List['MiniTraining']:
        mini_training_nodes = itertools.chain.from_iterable(
            tree_version.get_tree().get_all_nodes(types=set(MiniTrainingType.all())) for tree_version in tree_versions
        )
        return [MiniTrainingFactory.from_node(node) for node in mini_training_nodes]

    @classmethod
    def __persist_mini_trainings(cls, mini_trainings: List['MiniTraining']):
        repo = mini_trainig_repository.MiniTrainingRepository()
        return [repo.create(mini_training) for mini_training in mini_trainings]

    @classmethod
    def __create_groups(cls, tree_versions: List['ProgramTreeVersion']) -> List['Group']:
        nodes = itertools.chain.from_iterable(
            tree_version.get_tree().get_all_nodes() for tree_version in tree_versions
        )
        return [GroupFactory.from_node(node) for node in nodes if not node.is_learning_unit()]

    @classmethod
    def __persist_groups(cls, groups: List['Group']):
        repo = group_repository.GroupRepository()
        return [repo.create(group) for group in groups]

    @classmethod
    def create_specific_version_from_tree_version(
            cls,
            source_tree_version: 'ProgramTreeVersion',
            from_start_year: int = None,
            end_year: int = None,
            version_name: str = 'VERSION',
    ) -> List['ProgramTreeVersion']:
        identities = create_and_postpone_tree_specific_version_service \
            .create_and_postpone_program_tree_specific_version(
                CreateProgramTreeSpecificVersionCommand(
                    end_year=end_year or source_tree_version.end_year_of_existence,
                    offer_acronym=source_tree_version.entity_id.offer_acronym,
                    version_name=version_name,
                    start_year=from_start_year or source_tree_version.start_year,
                    transition_name=NOT_A_TRANSITION,
                    title_fr="",
                    title_en="",
                )
            )
        tree_versions = program_tree_version_repository.ProgramTreeVersionRepository().search(identities)
        for tree_version in tree_versions[1:]:
            tree_version.get_tree().authorized_relationships = tree_versions[0].get_tree().authorized_relationships
        return tree_versions

    @classmethod
    def create_transition_from_tree_version(
            cls,
            source_tree_version: 'ProgramTreeVersion',
            from_start_year: int = None,
            end_year: int = None,
            transition_name: str = 'TRANSITION',
    ) -> List['ProgramTreeVersion']:
        identities = create_and_postpone_tree_transition_version_service \
            .create_and_postpone_program_tree_transition_version(
                CreateProgramTreeTransitionVersionCommand(
                    end_year=end_year or source_tree_version.end_year_of_existence,
                    offer_acronym=source_tree_version.entity_id.offer_acronym,
                    version_name=source_tree_version.version_name,
                    start_year=from_start_year or source_tree_version.start_year,
                    from_year=from_start_year or source_tree_version.start_year,
                    transition_name=transition_name,
                    title_fr="",
                    title_en="",
                )
            )
        tree_versions = program_tree_version_repository.ProgramTreeVersionRepository().search(identities)
        for tree_version in tree_versions[1:]:
            tree_version.get_tree().authorized_relationships = tree_versions[0].get_tree().authorized_relationships
        return tree_versions


def build_tree_version(
        tree_data: Dict,
        year: int,
        start_year: int,
        end_year: Optional[int]
) -> 'ProgramTreeVersion':
    return ProgramTreeVersionFactory(tree=build_tree(tree_data, year, start_year, end_year), persist=True)


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


def build_sub_trees(tree_version: 'ProgramTreeVersion') -> List['ProgramTreeVersion']:
    nodes = tree_version.get_tree().root_node.get_all_children_as_nodes()
    group_nodes = (node for node in nodes if node.is_group())
    training_mini_training_nodes = (node for node in nodes if node.is_training() or node.is_mini_training())
    trees = [
        ProgramTreeFactory(
            root_node=node,
            authorized_relationships=tree_version.get_tree().authorized_relationships,
            persist=True
        ) for node in group_nodes
    ]
    return [
        ProgramTreeVersionFactory(
            tree__root_node=node,
            tree__authorized_relationships=tree_version.get_tree().authorized_relationships,
            tree__persist=True,
            persist=True
        ) for node in training_mini_training_nodes
    ]


def build_prerequisites(tree: 'ProgramTree', prerequisites_data: List):
    prerequisites = [
        PrerequisiteFactory().from_expression(
            prerequisite_expression, NodeIdentity(code, tree.root_node.year),
            tree.entity_id
        ) for code, prerequisite_expression in prerequisites_data
    ]
    return PrerequisitesFactory(context_tree=tree.entity_id, prerequisites=prerequisites)


def build_node(node_data: Dict, year: int, start_year: int, end_year: Optional[int], nodes_generated: Dict) -> 'Node':
    if node_data["code"] in nodes_generated:
        return nodes_generated[node_data["code"]]

    node_factory = get_node_factory(node_data["node_type"])
    node = node_factory(node_data, year, start_year, end_year)
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
    if node_type == NodeType.LEARNING_UNIT:
        return _build_node_learning_unit_year
    return _build_node_group_year


def _build_node_learning_unit_year(node_data: Dict, year, start_year, end_year) -> 'NodeLearningUnitYear':
    return NodeLearningUnitYearFactory(
        code=node_data["code"],
        title=node_data["title"],
        start_year=start_year,
        end_date=end_year,
        year=year,
    )


def _build_node_group_year(node_data: Dict, year, start_year, end_year) -> 'NodeGroupYear':
    return NodeGroupYearFactory(
        code=node_data["code"],
        title=node_data["title"],
        start_year=start_year,
        end_date=end_year,
        year=year,
        node_type=node_data["node_type"],
        version_name=node_data.get("version_name", STANDARD),
        transition_name=node_data.get("transition_name", NOT_A_TRANSITION),
    )
