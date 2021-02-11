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

from program_management.ddd.command import CopyTreeVersionToNextYearCommand
from program_management.ddd.service.write import bulk_copy_program_tree_version_content_service
from program_management.tests.ddd.factories.domain.program_tree.BACHELOR_1BA import ProgramTreeBachelorFactory
from program_management.tests.ddd.factories.domain.program_tree.program_tree_identity import ProgramTreeIdentityFactory
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory, \
    ProgramTreeVersionIdentityFactory
from program_management.tests.ddd.factories.repository.fake import get_fake_program_tree_repository, \
    get_fake_program_tree_version_repository
from testing.mocks import MockPatcherMixin


class TestBulkCopyProgramTreeVersion(MockPatcherMixin, TestCase):
    def setUp(self) -> None:
        self.tree_version = ProgramTreeVersionFactory(tree=ProgramTreeBachelorFactory(current_year=2020, end_year=2021))
        self.cmd = CopyTreeVersionToNextYearCommand(
            from_year=self.tree_version.tree.root_node.year,
            from_offer_acronym=self.tree_version.tree.root_node.title,
            from_offer_code=self.tree_version.tree.root_node.code,
            from_version_name=self.tree_version.version_name,
            from_is_transition=self.tree_version.is_transition,
        )

        self.fake_program_tree_version_repository = get_fake_program_tree_version_repository([self.tree_version])
        self.mock_repo(
            "program_management.ddd.repositories.program_tree_version.ProgramTreeVersionRepository",
            self.fake_program_tree_version_repository
        )
        self.fake_program_tree_repository = get_fake_program_tree_repository([self.tree_version.tree])
        self.mock_repo(
            "program_management.ddd.repositories.program_tree.ProgramTreeRepository",
            self.fake_program_tree_repository
        )

    def test_should_return_next_year_identity(self):
        result = bulk_copy_program_tree_version_content_service.bulk_copy_program_tree_version([self.cmd])
        expected_identity = self._get_next_year_tree_version_identity()
        self.assertListEqual(result, [expected_identity])

    def test_should_persist_next_year_tree_with_same_content(self):
        bulk_copy_program_tree_version_content_service.bulk_copy_program_tree_version([self.cmd])

        next_year_tree = self.fake_program_tree_repository.get(
            self._get_next_year_tree_identity()
        )

        self.assertCountEqual(
            [(node.code, node.year) for node in self.tree_version.tree.get_all_nodes()],
            [(node.code, node.year-1) for node in next_year_tree.get_all_nodes()]
        )

    def test_should_omit_nodes_that_have_end_date_inferior_to_next_year(self):
        self.tree_version.tree.get_node("1|22|32").end_date = 2020
        bulk_copy_program_tree_version_content_service.bulk_copy_program_tree_version([self.cmd])

        next_year_tree = self.fake_program_tree_repository.get(
            self._get_next_year_tree_identity()
        )

        self.assertTrue(
            len(self.tree_version.tree.get_all_nodes()) > len(next_year_tree.get_all_nodes())
        )

    def test_should_not_copy_content_for_tree_with_end_date_set_to_current_year(self):
        self.tree_version.end_year_of_existence = 2020
        self.tree_version.tree.root_node.end_year = 2020

        result = bulk_copy_program_tree_version_content_service.bulk_copy_program_tree_version([self.cmd])
        self.assertListEqual(result, [])

    def test_should_copy_prerequisites_to_next_year(self):
        bulk_copy_program_tree_version_content_service.bulk_copy_program_tree_version([self.cmd])

        next_year_tree = self.fake_program_tree_repository.get(
            self._get_next_year_tree_identity()
        )
        self.assertEqual(
            len(self.tree_version.tree.prerequisites.prerequisites),
            len(next_year_tree.prerequisites.prerequisites)
        )

    def test_should_not_copy_content_when_tree_next_year_already_exists_and_is_not_empty(self):
        first_copy_result = bulk_copy_program_tree_version_content_service.bulk_copy_program_tree_version([self.cmd])
        second_copy_result = bulk_copy_program_tree_version_content_service.bulk_copy_program_tree_version([self.cmd])
        self.assertListEqual([], second_copy_result)

    def _get_next_year_tree_version_identity(self):
        return ProgramTreeVersionIdentityFactory(
            offer_acronym=self.tree_version.entity_id.offer_acronym,
            year=self.tree_version.entity_id.year+1,
            version_name=self.tree_version.entity_id.version_name,
            is_transition=self.tree_version.entity_id.is_transition,

        )

    def _get_next_year_tree_identity(self):
        return ProgramTreeIdentityFactory(
            code=self.tree_version.tree.entity_id.code,
            year=self.tree_version.tree.entity_id.year+1,
        )
