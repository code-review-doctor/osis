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

from django.test import TestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from education_group.tests.ddd.factories.repository.fake import get_fake_group_repository
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory
from program_management.tests.ddd.factories.repository.fake import get_fake_program_tree_version_repository, \
    get_fake_program_tree_repository, get_fake_node_repository, get_fake_program_tree_version_identity_search
from testing.mocks import MockPatcherMixin
from program_management.ddd.business_types import *


class DDDTestCase(MockPatcherMixin, TestCase):
    def _init_fake_repos(self):
        self.fake_program_tree_version_repository = get_fake_program_tree_version_repository([])
        self.mock_repo(
            "program_management.ddd.repositories.program_tree_version.ProgramTreeVersionRepository",
            self.fake_program_tree_version_repository
        )

        self.fake_program_tree_repository = get_fake_program_tree_repository([])
        self.mock_repo(
            "program_management.ddd.repositories.program_tree.ProgramTreeRepository",
            self.fake_program_tree_repository
        )

        self.fake_node_repository = get_fake_node_repository([])
        self.mock_repo(
            "program_management.ddd.repositories.node.NodeRepository",
            self.fake_node_repository
        )

        self.fake_group_repository = get_fake_group_repository([])
        self.mock_repo(
            "education_group.ddd.repository.group.GroupRepository",
            self.fake_group_repository
        )

        self.fake_program_tree_version_identity_search = get_fake_program_tree_version_identity_search(
            self.fake_program_tree_version_repository
        )
        self.mock_repo(
            "program_management.ddd.domain.service.identity_search.ProgramTreeVersionIdentitySearch",
            self.fake_program_tree_version_identity_search
        )

    def add_tree_version_to_repo(self, tree_version: 'ProgramTreeVersion'):
        self.fake_program_tree_version_repository.root_entities.append(tree_version)
        self.add_tree_to_repo(tree_version.get_tree(), create_tree_version=False)

    def add_tree_to_repo(self, tree: 'ProgramTree', create_tree_version=True):
        self.fake_program_tree_repository.root_entities.append(tree)

        self.add_node_to_repo(tree.root_node, create_tree_version=create_tree_version, create_tree=False)
        for node in tree.root_node.get_all_children_as_nodes():
            self.add_node_to_repo(node, create_tree_version=True, create_tree=True)

    def add_node_to_repo(self, node: 'Node', create_tree_version=True, create_tree=True):
        self.fake_node_repository.root_entities.append(node)

        if node.is_learning_unit():
            return

        tree_version = ProgramTreeVersionFactory(
            tree__root_node=node,
            entity_id__version_name=node.version_name
        )
        if create_tree_version:
            self.fake_program_tree_version_repository.root_entities.append(
                tree_version
            )
        if create_tree:
            self.fake_program_tree_repository.root_entities.append(
                tree_version.tree
            )

    def assertRaisesBusinessException(self, exception, func, *args, **kwargs):
        with self.assertRaises(MultipleBusinessExceptions) as e:
            func(*args, **kwargs)
        class_exceptions = [exc.__class__ for exc in e.exception.exceptions]
        self.assertIn(exception, class_exceptions)
