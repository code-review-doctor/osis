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

import attr

from base.models.enums.link_type import LinkTypes
from infrastructure.messages_bus import message_bus_instance
from program_management.ddd.command import BulkUpdateLinkCommand, UpdateLinkCommand
from program_management.ddd.domain.exception import BulkUpdateLinkException, InvalidBlockException, \
    RelativeCreditShouldBeGreaterOrEqualsThanZero, RelativeCreditShouldBeLowerOrEqualThan999, \
    ReferenceLinkNotAllowedWithLearningUnitException, ChildTypeNotAuthorizedException
from program_management.ddd.domain.report import ReportIdentity
from program_management.ddd.domain.report_events import CannotPostponeLinkToNextYearAsConsistencyError
from program_management.ddd.repositories.report import ReportRepository
from program_management.tests.ddd.factories.domain.program_tree_version.training.OSIS1BA import OSIS1BAFactory
from testing.testcases import DDDTestCase


class TestUpdateLink(DDDTestCase):
    def setUp(self) -> None:
        super().setUp()
        tree_versions = OSIS1BAFactory()
        self.tree, *self.next_year_trees = [tree_version.get_tree() for tree_version in tree_versions]
        self.cmd = UpdateLinkCommand(
            block="123",
            parent_node_code=self.tree.root_node.code,
            parent_node_year=self.tree.root_node.year,
            child_node_code=self.tree.root_node.children_as_nodes[0].code,
            child_node_year=self.tree.root_node.children_as_nodes[0].year,
            link_type=None,
            comment="A comment",
            comment_english="A comment in english",
            relative_credits=20,
            is_mandatory=False,
            access_condition=False
        )

    def test_block_value_should_be_an_increasing_sequence_of_digit_between_1_and_6(self):
        cmd = attr.evolve(self.cmd, block="158")

        with self.assertRaisesBusinessException(BulkUpdateLinkException) as e:
            message_bus_instance.invoke(self._generate_bulk_cmd(cmd))

        self.assert_exception_in(e.exception, cmd, InvalidBlockException)

    def test_cannot_have_relative_credits_lower_than_0(self):
        cmd = attr.evolve(self.cmd, relative_credits=-1)

        with self.assertRaisesBusinessException(BulkUpdateLinkException) as e:
            message_bus_instance.invoke(self._generate_bulk_cmd(cmd))

        self.assert_exception_in(e.exception, cmd, RelativeCreditShouldBeGreaterOrEqualsThanZero)

    def test_cannot_have_relative_credits_greater_than_999(self):
        cmd = attr.evolve(self.cmd, relative_credits=1000)

        with self.assertRaisesBusinessException(BulkUpdateLinkException) as e:
            message_bus_instance.invoke(self._generate_bulk_cmd(cmd))

        self.assert_exception_in(e.exception, cmd, RelativeCreditShouldBeLowerOrEqualThan999)

    def test_cannot_set_link_type_as_reference_for_link_with_a_learning_unit_as_a_child(self):
        link_with_learning_unit = next(link for link in self.tree.get_all_links() if link.child.is_learning_unit())
        cmd = attr.evolve(
            self.cmd,
            link_type=LinkTypes.REFERENCE.name,
            parent_node_code=link_with_learning_unit.parent.code,
            parent_node_year=link_with_learning_unit.parent.year,
            child_node_code=link_with_learning_unit.child.code,
            child_node_year=link_with_learning_unit.child.year,
        )

        with self.assertRaisesBusinessException(BulkUpdateLinkException) as e:
            message_bus_instance.invoke(self._generate_bulk_cmd(cmd, tree_code=link_with_learning_unit.parent.code))

        self.assert_exception_in(e.exception, cmd, ReferenceLinkNotAllowedWithLearningUnitException)

    def test_cannot_set_link_as_reference_when_children_of_child_are_not_valid_children_type_for_parent(self):
        cmd = attr.evolve(self.cmd, link_type=LinkTypes.REFERENCE.name)

        with self.assertRaisesBusinessException(BulkUpdateLinkException) as e:
            message_bus_instance.invoke(self._generate_bulk_cmd(cmd))

        self.assert_exception_in(e.exception, cmd, ChildTypeNotAuthorizedException)

    def test_always_reference_link_between_minor_major_list_choice_and_minor_or_major_or_deepening(self):
        link_with_minor = next(link for link in self.tree.get_all_links() if link.child.is_minor_major_deepening())

        cmd = attr.evolve(
            self.cmd,
            link_type=None,
            parent_node_code=link_with_minor.parent.code,
            parent_node_year=link_with_minor.parent.year,
            child_node_code=link_with_minor.child.code,
            child_node_year=link_with_minor.child.year,
        )

        message_bus_instance.invoke(
            self._generate_bulk_cmd(cmd, tree_code=link_with_minor.parent.code, tree_year=link_with_minor.parent.year)
        )
        self.assertEqual(link_with_minor.link_type, LinkTypes.REFERENCE)

    def test_should_update_link_attributes(self):
        result = message_bus_instance.invoke(self._generate_bulk_cmd(self.cmd))[0]

        self.assertEqual(result.link_type, self.cmd.link_type)
        self.assertEqual(result.access_condition, self.cmd.access_condition)
        self.assertEqual(result.is_mandatory, self.cmd.is_mandatory)
        self.assertEqual(result.block, self.cmd.block)
        self.assertEqual(result.comment, self.cmd.comment)
        self.assertEqual(result.comment_english, self.cmd.comment_english)
        self.assertEqual(result.relative_credits, self.cmd.relative_credits)

    def test_should_report_link_modifications(self):
        bulk_update_cmd = self._generate_bulk_cmd(self.cmd)

        message_bus_instance.invoke(bulk_update_cmd)

        conflict_report = ReportRepository().get(ReportIdentity(bulk_update_cmd.transaction_id))
        self.assertTrue(isinstance(conflict_report.warnings[0], CannotPostponeLinkToNextYearAsConsistencyError))

        link_with_common_core_next_year = self.next_year_trees[0].root_node.children[0]

        self.assertNotEqual(link_with_common_core_next_year.is_mandatory, self.cmd.is_mandatory)
        self.assertNotEqual(link_with_common_core_next_year.block, self.cmd.block)
        self.assertNotEqual(link_with_common_core_next_year.comment, self.cmd.comment)
        self.assertNotEqual(link_with_common_core_next_year.comment_english, self.cmd.comment_english)
        self.assertNotEqual(link_with_common_core_next_year.relative_credits, self.cmd.relative_credits)

    def test_cannot_convert_mandatory_child_link_to_reference(self):
        cmd = attr.evolve(self.cmd, link_type=LinkTypes.REFERENCE.name)

        with self.assertRaisesBusinessException(BulkUpdateLinkException) as e:
            message_bus_instance.invoke(self._generate_bulk_cmd(cmd))

        self.assert_exception_in(e.exception, cmd, ChildTypeNotAuthorizedException)

    def assert_exception_in(self, bulk_exceptions: BulkUpdateLinkException, cmd: UpdateLinkCommand, exception_cls):
        cmd_exceptions = bulk_exceptions.exceptions[cmd].exceptions
        self.assertIn(
            exception_cls,
            [e.__class__ for e in cmd_exceptions]
        )

    def _generate_bulk_cmd(self, cmd, tree_code=None, tree_year=None):
        return BulkUpdateLinkCommand(
            working_tree_code=tree_code or self.tree.root_node.code,
            working_tree_year=tree_year or self.tree.root_node.year,
            update_link_cmds=[cmd]
        )
