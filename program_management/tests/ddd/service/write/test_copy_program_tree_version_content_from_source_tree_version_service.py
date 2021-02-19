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
from django.test import TestCase

from program_management.ddd.command import CopyProgramTreeVersionContentFromSourceTreeVersionCommand
from program_management.ddd.service.write.copy_program_tree_version_content_from_source_tree_version_service import \
    copy_program_tree_version_content_from_source_tree_version
from program_management.tests.ddd.factories.domain.program_tree.BACHELOR_1BA import ProgramTreeBachelorFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory, \
    StandardProgramTreeVersionFactory
from program_management.tests.ddd.factories.repository.fake import get_fake_program_tree_version_repository, \
    get_fake_program_tree_repository
from testing.mocks import MockPatcherMixin


class TestCopyProgramTreeVersionContentFromSourceTreeVersion(MockPatcherMixin, TestCase):
    def setUp(self) -> None:
        self.standard_tree_version = StandardProgramTreeVersionFactory(
            tree=ProgramTreeBachelorFactory(current_year=2020, end_year=2021)
        )
        self.transition_tree_version = StandardProgramTreeVersionFactory(
            transition=True,
            tree__root_node__title=self.standard_tree_version.entity_id.offer_acronym,
            tree__root_node__year=2021
        )
        self.cmd = CopyProgramTreeVersionContentFromSourceTreeVersionCommand(
            from_year=self.standard_tree_version.entity_id.year,
            from_offer_acronym=self.standard_tree_version.entity_id.offer_acronym,
            from_version_name=self.standard_tree_version.entity_id.version_name,
            from_transition_name=self.standard_tree_version.entity_id.transition_name,
            to_year=self.transition_tree_version.entity_id.year,
            to_offer_acronym=self.transition_tree_version.entity_id.offer_acronym,
            to_version_name=self.transition_tree_version.entity_id.version_name,
            to_transition_name=self.transition_tree_version.entity_id.transition_name
        )

        self.fake_program_tree_version_repository = get_fake_program_tree_version_repository(
            [self.standard_tree_version, self.transition_tree_version]
        )
        self.mock_repo(
            "program_management.ddd.repositories.program_tree_version.ProgramTreeVersionRepository",
            self.fake_program_tree_version_repository
        )
        self.fake_program_tree_repository = get_fake_program_tree_repository(
            [self.standard_tree_version.tree, self.transition_tree_version.tree]
        )
        self.mock_repo(
            "program_management.ddd.repositories.program_tree.ProgramTreeRepository",
            self.fake_program_tree_repository
        )

    def test_should_return_copied_tree_identity(self):
        result = copy_program_tree_version_content_from_source_tree_version(self.cmd)
        expected_identity = self.transition_tree_version.entity_id
        self.assertEqual(expected_identity, result)
