# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from collections import namedtuple
from typing import Any, Optional, List

import mock
from django.test import TestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from education_group.tests.ddd.factories.repository.fake import get_fake_group_repository, \
    get_fake_mini_training_repository, get_fake_training_repository, FakeGroupRepository
from program_management.ddd.business_types import *
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory
from program_management.tests.ddd.factories.repository.fake import get_fake_program_tree_version_repository, \
    get_fake_program_tree_repository, get_fake_node_repository, FakeNodeRepository, FakeProgramTreeVersionRepository, \
    FakeProgramTreeRepository


class DDDTestCase(TestCase):
    starting_academic_year_year = 2020

    def setUp(self) -> None:
        super().setUp()
        self.mock_service(
            "base.models.academic_year.starting_academic_year",
            return_value=namedtuple("academic_year", "year")(self.starting_academic_year_year)
        )
        self._init_education_group_app_repo()
        self._init_program_management_app_repo()

    def _init_education_group_app_repo(self):
        self.fake_training_repository = get_fake_training_repository([])
        self.fake_mini_training_repository = get_fake_mini_training_repository([])
        self.fake_group_repository = get_fake_group_repository([])
        self.mock_repo("education_group.ddd.repository.group.GroupRepository", self.fake_group_repository)
        self.mock_repo("education_group.ddd.repository.training.TrainingRepository", self.fake_training_repository)
        self.mock_repo(
            "education_group.ddd.repository.mini_training.MiniTrainingRepository",
            self.fake_mini_training_repository
        )

    def _init_program_management_app_repo(self):
        self.fake_node_repository = get_fake_node_repository([])
        self.fake_program_tree_repository = get_fake_program_tree_repository([])
        self.fake_program_tree_version_repository = get_fake_program_tree_version_repository([])
        self.mock_repo(
            "program_management.ddd.repositories.node.NodeRepository",
            self.fake_node_repository
        )
        self.mock_repo(
            "program_management.ddd.repositories.program_tree.ProgramTreeRepository",
            self.fake_program_tree_repository
        )
        self.mock_repo(
            "program_management.ddd.repositories.program_tree_version.ProgramTreeVersionRepository",
            self.fake_program_tree_version_repository
        )

        self.mock_service(
            "program_management.ddd.domain.service.identity_search.NodeIdentitySearch.get_from_element_id",
            side_effect=get_from_element_id
        )

        self.mock_service(
            "program_management.ddd.domain.service.node_identities_search.NodeIdentitiesSearch.search_from_code",
            side_effect=get_node_identities_from_code
        )

        self.mock_service(
            "program_management.ddd.domain.service.identity_search.ProgramTreeVersionIdentitySearch."
            "get_from_node_identities",
            side_effect=get_program_tree_version_identity_from_node_identities
        )

        self.mock_service(
            "education_group.ddd.domain.service.abbreviated_title_exist.CheckAcronymExist.exists",
            side_effect=check_acronym_exists
        )

    def tearDown(self) -> None:
        self.fake_group_repository._groups = list()
        self.fake_mini_training_repository._mini_trainings = list()
        self.fake_training_repository._trainings = list()

        self.fake_node_repository._nodes = list()
        self.fake_program_tree_repository._trees = list()
        self.fake_program_tree_version_repository._trees_version = list()

    def mock_repo(self, repository_path: 'str', fake_repo: 'Any') -> mock.Mock:
        repository_patcher = mock.patch(repository_path, new=fake_repo)
        self.addCleanup(repository_patcher.stop)

        return repository_patcher.start()

    def mock_service(self, service_path: str, return_value: 'Any' = None, side_effect: 'Any' = None) -> mock.Mock:
        service_patcher = mock.patch(service_path, return_value=return_value, side_effect=side_effect)
        self.addCleanup(service_patcher.stop)

        return service_patcher.start()

    def add_tree_version_to_repo(self, tree_version: 'ProgramTreeVersion'):
        self.fake_program_tree_version_repository._trees_version.append(tree_version)
        self.add_tree_to_repo(tree_version.get_tree(), create_tree_version=False)

    def add_tree_to_repo(self, tree: 'ProgramTree', create_tree_version=True):
        self.fake_program_tree_repository._trees.append(tree)

        self.add_node_to_repo(tree.root_node, create_tree_version=create_tree_version, create_tree=False)
        for node in tree.root_node.get_all_children_as_nodes():
            self.add_node_to_repo(node, create_tree_version=True, create_tree=True)

    def add_node_to_repo(self, node: 'Node', create_tree_version=True, create_tree=True):
        self.fake_node_repository._nodes.append(node)

        if node.is_learning_unit():
            return

        tree_version = ProgramTreeVersionFactory(
            tree__root_node=node,
            entity_id__version_name=node.version_name
        )
        if create_tree_version:
            self.fake_program_tree_version_repository._trees_version.append(
                tree_version
            )
        if create_tree:
            self.fake_program_tree_repository._trees.append(
                tree_version.tree
            )

    def assertRaisesBusinessException(self, exception, func, *args, **kwargs):
        with self.assertRaises(MultipleBusinessExceptions) as e:
            func(*args, **kwargs)
        class_exceptions = [exc.__class__ for exc in e.exception.exceptions]
        self.assertIn(exception, class_exceptions)


def get_from_element_id(element_id: int) -> Optional['NodeIdentity']:
    repo = FakeNodeRepository()
    return next(
        (node for node in repo._nodes if node.node_id == element_id),
        None
    )


def get_node_identities_from_code(group_code: str) -> List['NodeIdentity']:
    repo = FakeProgramTreeRepository()
    return [tree.root_node.entity_id for tree in repo._trees if tree.root_node.code == group_code]


def get_program_tree_version_identity_from_node_identities(
        node_identities: List['NodeIdentity']
) -> List['ProgramTreeVersionIdentity']:
    repo = FakeProgramTreeVersionRepository()
    node_identities_set = set(node_identities)
    return [
        tree_version.entity_id for tree_version in repo._trees_version
        if tree_version.get_tree().root_node.entity_id in node_identities_set
    ]


def check_acronym_exists(abbreviated_title: str) -> bool:
    repo = FakeGroupRepository()
    return any(group for group in repo._groups if group.abbreviated_title == abbreviated_title)
