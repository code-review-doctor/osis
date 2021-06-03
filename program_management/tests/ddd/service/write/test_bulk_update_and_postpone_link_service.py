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
from unittest.mock import patch

from base.models.authorized_relationship import AuthorizedRelationshipObject
from base.models.enums.education_group_types import TrainingType, GroupType, MiniTrainingType
from base.models.enums.link_type import LinkTypes
from program_management.ddd.command import BulkUpdateLinkCommand, UpdateLinkCommand
from program_management.ddd.domain import exception
from program_management.ddd.domain.exception import BulkUpdateLinkException
from program_management.ddd.domain.program_tree import ProgramTreeBuilder
from program_management.ddd.domain.report import ReportIdentity
from program_management.ddd.domain.report_events import CannotPostponeLinkToNextYearAsConsistencyError
from program_management.ddd.domain.service.search_program_trees_in_future import SearchProgramTreesInFuture
from program_management.ddd.repositories.report import ReportRepository
from program_management.ddd.service.write import bulk_update_link_service
from program_management.models.enums.node_type import NodeType
from program_management.tests.ddd.factories.domain.program_tree_version.training.OSIS1BA import OSIS1BAFactory
from program_management.tests.ddd.factories.program_tree import tree_builder
from testing.testcases import DDDTestCase


# class TestUpdateLink(DDDTestCase):
#     def setUp(self) -> None:
#         super().setUp()
#         self.tree = OSIS1BAFactory()[0].tree
#         self.cmd = UpdateLinkCommand(
#             block="123",
#             parent_node_code=self.tree.root_node.code,
#             parent_node_year=self.tree.root_node.year,
#             child_node_code=self.tree.root_node.children_as_nodes[0].code,
#             child_node_year=self.tree.root_node.children_as_nodes[0].year,
#             link_type=None,
#             comment="A comment",
#             comment_english="A comment in english",
#             relative_credits=20,
#             is_mandatory=False,
#             access_condition=False
#         )
#
#     def test_block_value_should_be_an_increasing_sequence_of_digit_between_1_and_6(self):
#         cmd = attr.evolve(self.cmd, block="158")
#
#         with self.assertRaisesBusinessException(InvalidBlockException):
#             update_link_service.update_link(cmd)
#
#     def test_cannot_have_relative_credits_lower_than_0(self):
#         cmd = attr.evolve(self.cmd, relative_credits=-1)
#
#         with self.assertRaisesBusinessException(RelativeCreditShouldBeGreaterOrEqualsThanZero):
#             update_link_service.update_link(cmd)
#
#     def test_cannot_have_relative_credits_greater_than_999(self):
#         cmd = attr.evolve(self.cmd, relative_credits=1000)
#
#         with self.assertRaisesBusinessException(RelativeCreditShouldBeLowerOrEqualThan999):
#             update_link_service.update_link(cmd)
#
#     def test_cannot_set_link_type_as_reference_for_link_with_a_learning_unit_as_a_child(self):
#         link_with_learning_unit = next(link for link in self.tree.get_all_links() if link.child.is_learning_unit())
#         cmd = attr.evolve(
#             self.cmd,
#             link_type=LinkTypes.REFERENCE.name,
#             parent_node_code=link_with_learning_unit.parent.code,
#             parent_node_year=link_with_learning_unit.parent.year,
#             child_node_code=link_with_learning_unit.child.code,
#             child_node_year=link_with_learning_unit.child.year,
#         )
#
#         with self.assertRaisesBusinessException(ReferenceLinkNotAllowedWithLearningUnitException):
#             update_link_service.update_link(cmd)
#
#     def test_always_reference_link_between_minor_major_list_choice_and_minor_or_major_or_deepening(self):
#         link_with_minor = next(link for link in self.tree.get_all_links() if link.child.is_minor_major_deepening())
#
#         cmd = attr.evolve(
#             self.cmd,
#             link_type=None,
#             parent_node_code=link_with_minor.parent.code,
#             parent_node_year=link_with_minor.parent.year,
#             child_node_code=link_with_minor.child.code,
#             child_node_year=link_with_minor.child.year,
#         )
#
#         update_link_service.update_link(cmd)
#         self.assertEqual(link_with_minor.link_type, LinkTypes.REFERENCE)
#
#     def test_cannot_set_link_as_reference_when_children_of_child_are_not_valid_children_type_for_parent(self):
#         cmd = attr.evolve(self.cmd, link_type=LinkTypes.REFERENCE.name)
#
#         with self.assertRaisesBusinessException(ChildTypeNotAuthorizedException):
#             update_link_service.update_link(cmd)
#
#     def test_should_update_link_attributes(self):
#         result = update_link_service.update_link(self.cmd)
#
#         self.assertEqual(result.link_type, self.cmd.link_type)
#         self.assertEqual(result.access_condition, self.cmd.access_condition)
#         self.assertEqual(result.is_mandatory, self.cmd.is_mandatory)
#         self.assertEqual(result.block, self.cmd.block)
#         self.assertEqual(result.comment, self.cmd.comment)
#         self.assertEqual(result.comment_english, self.cmd.comment_english)
#         self.assertEqual(result.relative_credits, self.cmd.relative_credits)
#
#     def test_cannot_convert_mandatory_child_link_to_reference(self):
#         cmd = attr.evolve(self.cmd, link_type=LinkTypes.REFERENCE.name)
#
#         with self.assertRaisesBusinessException(ChildTypeNotAuthorizedException):
#             update_link_service.update_link(cmd)

@patch(
    "base.business.academic_calendar.AcademicEventCalendarHelper.get_target_years_opened",
    return_value=[2016]
)
class TestUpdateLink(DDDTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.tree = OSIS1BAFactory(start_year=2016, end_year=2018)

    def test_failure_when_block_value_is_not_a_increasing_sequence_of_digits_between_1_and_6(self, mock_calendar):
        block_inputs = ["158", "265", "49"]
        for block_input in block_inputs:
            cmd_with_invalid_block_value = UpdateLinkCommand(
                block=block_input,
                parent_node_code=self.tree.root_node.code,
                parent_node_year=self.tree.root_node.year,
                child_node_code=self.tree.root_node.children_as_nodes[0].code,
                child_node_year=self.tree.root_node.children_as_nodes[0].year,
                link_type=None,
                comment="",
                comment_english="english cvommen",
                relative_credits=10,
                access_condition=True,
                is_mandatory=False
            )
            invalid_bulk_update_cmd = BulkUpdateLinkCommand(
                working_tree_code=self.tree.root_node.code,
                working_tree_year=self.tree.root_node.year,
                update_link_cmds=[cmd_with_invalid_block_value]
            )

            with self.assertRaises(BulkUpdateLinkException) as e:
                bulk_update_link_service.bulk_update_and_postpone_links(
                    invalid_bulk_update_cmd,
                    self.fake_program_tree_repository,
                    ReportRepository()
                )
            self.assertIsInstance(
                next(iter(e.exception.exceptions[cmd_with_invalid_block_value].exceptions)),
                exception.InvalidBlockException
            )

    def test_failure_when_relative_credits_less_or_equal_to_0(self, mock_calendar):
        cmd_with_invalid_relative_credits_value = UpdateLinkCommand(
            relative_credits=-1,
            parent_node_code=self.tree.root_node.code,
            parent_node_year=self.tree.root_node.year,
            child_node_code=self.tree.root_node.children_as_nodes[0].code,
            child_node_year=self.tree.root_node.children_as_nodes[0].year,
            link_type=None,
            comment="",
            comment_english="english cvommen",
            access_condition=True,
            is_mandatory=False,
            block="123"
        )
        invalid_bulk_update_cmd = BulkUpdateLinkCommand(
            working_tree_code=self.tree.root_node.code,
            working_tree_year=self.tree.root_node.year,
            update_link_cmds=[cmd_with_invalid_relative_credits_value]
        )

        with self.assertRaises(BulkUpdateLinkException) as e:
            bulk_update_link_service.bulk_update_and_postpone_links(
                invalid_bulk_update_cmd,
                self.fake_program_tree_repository,
                ReportRepository()
            )

        self.assertIsInstance(
            next(iter(e.exception.exceptions[cmd_with_invalid_relative_credits_value].exceptions)),
            exception.RelativeCreditShouldBeGreaterOrEqualsThanZero
        )

    def test_failure_when_relative_credits_superior_to_999(self, mock_calendar):
        cmd_with_invalid_relative_credits_value = UpdateLinkCommand(
            relative_credits=1000, parent_node_code=self.tree.root_node.code,
            parent_node_year=self.tree.root_node.year,
            child_node_code=self.tree.root_node.children_as_nodes[0].code,
            child_node_year=self.tree.root_node.children_as_nodes[0].year,
            link_type=None,
            comment="",
            comment_english="english cvommen",
            access_condition=True,
            is_mandatory=False,
            block="123"
        )
        invalid_bulk_update_cmd = BulkUpdateLinkCommand(
            working_tree_code=self.tree.root_node.code,
            working_tree_year=self.tree.root_node.year,
            update_link_cmds=[cmd_with_invalid_relative_credits_value]
        )

        with self.assertRaises(BulkUpdateLinkException) as e:
            bulk_update_link_service.bulk_update_and_postpone_links(
                invalid_bulk_update_cmd,
                self.fake_program_tree_repository,
                ReportRepository()
            )

        self.assertIsInstance(
            next(iter(e.exception.exceptions[cmd_with_invalid_relative_credits_value].exceptions)),
            exception.RelativeCreditShouldBeLowerOrEqualThan999
        )

    def test_failure_when_reference_link_with_learning_unit_child_node(self, mock_calendar):
        cmd_with_invalid_reference_link = UpdateLinkCommand(
            link_type=LinkTypes.REFERENCE.name,
            parent_node_code=self.tree.root_node.code,
            parent_node_year=self.tree.root_node.year,
            child_node_code=self.tree.root_node.children_as_nodes[2].code,
            child_node_year=self.tree.root_node.children_as_nodes[2].year,
            comment="",
            comment_english="english cvommen",
            relative_credits=10,
            access_condition=True,
            is_mandatory=False,
            block="123"
        )
        invalid_bulk_cmd = BulkUpdateLinkCommand(
            working_tree_code=self.tree.root_node.code,
            working_tree_year=self.tree.root_node.year,
            update_link_cmds=[cmd_with_invalid_reference_link]
        )

        with self.assertRaises(BulkUpdateLinkException) as e:
            bulk_update_link_service.bulk_update_and_postpone_links(
                invalid_bulk_cmd,
                self.fake_program_tree_repository,
                ReportRepository()
            )

        self.assertIsInstance(
            next(iter(e.exception.exceptions[cmd_with_invalid_reference_link].exceptions)),
            exception.ReferenceLinkNotAllowedWithLearningUnitException
        )

    def test_always_set_link_type_to_reference_between_minor_list_and_minor(self, mock_calendar):
        minor_list_choice_tree_data = {
            "node_type": GroupType.MINOR_LIST_CHOICE,
            "children": [
                {"node_type": MiniTrainingType.ACCESS_MINOR}
            ]
        }
        minor_list_choice_tree = tree_builder(minor_list_choice_tree_data)
        self.fake_program_tree_repository.create(minor_list_choice_tree)

        cmd_with_invalid_reference_link = BulkUpdateLinkCommand(
            working_tree_code=minor_list_choice_tree.root_node.code,
            working_tree_year=minor_list_choice_tree.root_node.year,
            update_link_cmds=[UpdateLinkCommand(
                link_type=None,
                parent_node_code=minor_list_choice_tree.root_node.code,
                parent_node_year=minor_list_choice_tree.root_node.year,
                child_node_code=minor_list_choice_tree.root_node.children_as_nodes[0].code,
                child_node_year=minor_list_choice_tree.root_node.children_as_nodes[0].year,
                comment="",
                comment_english="english cvommen",
                relative_credits=10,
                access_condition=True,
                is_mandatory=False
            )]
        )

        bulk_update_link_service.bulk_update_and_postpone_links(
            cmd_with_invalid_reference_link,
            self.fake_program_tree_repository,
            ReportRepository()
        )
        self.assertEqual(
            minor_list_choice_tree.root_node.children[0].link_type,
            LinkTypes.REFERENCE
        )

    def test_reference_link_always_valid_between_minor_and_list_minor(self, mock_calendar):
        minor_list_choice_tree_data = {
            "node_type": GroupType.MINOR_LIST_CHOICE,
            "children": [
                {
                    "node_type": MiniTrainingType.ACCESS_MINOR,
                    "children": [
                        {"node_type": NodeType.LEARNING_UNIT}
                    ]
                }
            ]
        }
        minor_list_choice_tree = tree_builder(minor_list_choice_tree_data)
        self.fake_program_tree_repository.create(minor_list_choice_tree)

        cmd = BulkUpdateLinkCommand(
            working_tree_code=minor_list_choice_tree.root_node.code,
            working_tree_year=minor_list_choice_tree.root_node.year,
            update_link_cmds=[UpdateLinkCommand(
                link_type=LinkTypes.REFERENCE.name,
                parent_node_code=minor_list_choice_tree.root_node.code,
                parent_node_year=minor_list_choice_tree.root_node.year,
                child_node_code=minor_list_choice_tree.root_node.children_as_nodes[0].code,
                child_node_year=minor_list_choice_tree.root_node.children_as_nodes[0].year,
                comment="",
                comment_english="english cvommen",
                access_condition=True,
                is_mandatory=False,
                block="123",
                relative_credits=10
            )]
        )

        self.assertTrue(bulk_update_link_service.bulk_update_and_postpone_links(
            cmd,
            self.fake_program_tree_repository,
            ReportRepository()
        ))

    def test_failure_when_reference_but_children_of_node_to_add_are_not_valid_relationships_to_parent(
            self,
            mock_calendar
    ):
        cmd_with_invalid_reference_link = UpdateLinkCommand(
            link_type=LinkTypes.REFERENCE.name,
            parent_node_code=self.tree.root_node.code,
            parent_node_year=self.tree.root_node.year,
            child_node_code=self.tree.root_node.children_as_nodes[0].code,
            child_node_year=self.tree.root_node.children_as_nodes[0].year,
            comment="",
            comment_english="english cvommen",
            access_condition=True,
            is_mandatory=False,
            block="123",
            relative_credits=10
        )
        invalid_bulk_cmd = BulkUpdateLinkCommand(
            working_tree_code=self.tree.root_node.code,
            working_tree_year=self.tree.root_node.year,
            update_link_cmds=[cmd_with_invalid_reference_link]
        )

        with self.assertRaises(BulkUpdateLinkException) as e:
            bulk_update_link_service.bulk_update_and_postpone_links(
                invalid_bulk_cmd,
                self.fake_program_tree_repository,
                ReportRepository()
            )

        self.assertIsInstance(
            next(iter(e.exception.exceptions[cmd_with_invalid_reference_link].exceptions)),
            exception.ChildTypeNotAuthorizedException
        )

    def test_failure_when_successive_reference_links_and_reference_children_type_not_valid_for_parent(
            self,
            mock_calendar
    ):
        successive_reference_link_tree_data = {
            "node_type": GroupType.COMPLEMENTARY_MODULE,
            "children": [
                {
                    "node_type": GroupType.SUB_GROUP,
                    "children": [
                        {
                            "node_type": GroupType.SUB_GROUP,
                            "link_data": {"link_type": LinkTypes.REFERENCE},
                            "children": [{"node_type": NodeType.LEARNING_UNIT}]
                        }
                    ]
                }
            ]
        }
        tree_with_successive_reference_link = tree_builder(successive_reference_link_tree_data)
        self.fake_program_tree_repository.create(tree_with_successive_reference_link)

        invalid_update_link_cmd = UpdateLinkCommand(
            link_type=LinkTypes.REFERENCE.name,
            parent_node_code=tree_with_successive_reference_link.root_node.code,
            parent_node_year=tree_with_successive_reference_link.root_node.year,
            child_node_code=tree_with_successive_reference_link.root_node.children_as_nodes[0].code,
            child_node_year=tree_with_successive_reference_link.root_node.children_as_nodes[0].year,
            comment="",
            comment_english="english cvommen",
            access_condition=True,
            is_mandatory=False,
            block="123",
            relative_credits=10
        )
        invalid_bulk_cmd = BulkUpdateLinkCommand(
            working_tree_code=tree_with_successive_reference_link.root_node.code,
            working_tree_year=tree_with_successive_reference_link.root_node.year,
            update_link_cmds=[invalid_update_link_cmd]
        )

        with self.assertRaises(BulkUpdateLinkException) as e:
            bulk_update_link_service.bulk_update_and_postpone_links(
                invalid_bulk_cmd,
                self.fake_program_tree_repository,
                ReportRepository()
            )

        self.assertIsInstance(
            next(iter(e.exception.exceptions[invalid_update_link_cmd].exceptions)),
            exception.ChildTypeNotAuthorizedException
        )

    def test_update_link_properties(self, mock_calendar):
        update_link_command = UpdateLinkCommand(
            parent_node_code=self.tree.root_node.code,
            parent_node_year=self.tree.root_node.year,
            child_node_code=self.tree.root_node.children_as_nodes[1].code,
            child_node_year=self.tree.root_node.children_as_nodes[1].year,
            comment='Un commentaire', comment_english='This is a comment',
            relative_credits=5,
        )
        valid_cmd = BulkUpdateLinkCommand(
            working_tree_code=self.tree.root_node.code,
            working_tree_year=self.tree.root_node.year,
            update_link_cmds=[update_link_command]
        )
        result = bulk_update_link_service.bulk_update_and_postpone_links(
            valid_cmd,
            self.fake_program_tree_repository,
            ReportRepository()
        )[0]
        self.assertEqual(result.link_type, update_link_command.link_type)
        self.assertEqual(result.access_condition, update_link_command.access_condition)
        self.assertEqual(result.is_mandatory, update_link_command.is_mandatory)
        self.assertEqual(result.block, update_link_command.block)
        self.assertEqual(result.comment, update_link_command.comment)
        self.assertEqual(result.comment_english, update_link_command.comment_english)
        self.assertEqual(result.relative_credits, update_link_command.relative_credits)

    def test_failure_if_maximum_children_reached(self, mock_calendar):
        tree_data = {
            "node_type": TrainingType.BACHELOR,
            "end_year": 2018,
            "children": [
                {
                    "node_type": GroupType.COMMON_CORE,
                    "children": [{"node_type": GroupType.MINOR_LIST_CHOICE}]
                },

                {"node_type": GroupType.MINOR_LIST_CHOICE}
            ]
        }
        tree = tree_builder(tree_data)
        self.fake_program_tree_repository.create(tree)
        tree.authorized_relationships.update(
            TrainingType.BACHELOR,
            GroupType.MINOR_LIST_CHOICE,
            max_count_authorized=1

        )

        invalid_update_link_cmd = UpdateLinkCommandFactory(
            link_type=LinkTypes.REFERENCE.name,
            parent_node_code=tree.root_node.code,
            parent_node_year=tree.root_node.year,
            child_node_code=tree.root_node.children_as_nodes[0].code,
            child_node_year=tree.root_node.children_as_nodes[0].year,
        )
        invalid_bulk_update_cmd = BulkUpdateLinkCommand(
            working_tree_code=tree.root_node.code,
            working_tree_year=tree.root_node.year,
            update_link_cmds=[invalid_update_link_cmd]
        )

        with self.assertRaises(BulkUpdateLinkException) as e:
            bulk_update_link_service.bulk_update_and_postpone_links(
                invalid_bulk_update_cmd,
                self.fake_program_tree_repository,
                ReportRepository()
            )

        self.assertIsInstance(
            next(iter(e.exception.exceptions[invalid_update_link_cmd].exceptions)),
            exception.MaximumChildTypesReachedException
        )

    def test_cannot_convert_mandatory_child_link_to_reference(self, mock_calendar):
        self.tree.authorized_relationships.update(
            TrainingType.BACHELOR,
            GroupType.COMMON_CORE,
            max_count_authorized=1,
            min_count_authorized=1,
        )
        self.tree.authorized_relationships.authorized_relationships.append(
            AuthorizedRelationshipObject(
                parent_type=TrainingType.BACHELOR,
                child_type=GroupType.SUB_GROUP,
                min_count_authorized=0,
                max_count_authorized=None
            )
        )

        update_link_cmd = UpdateLinkCommandFactory(
            parent_node_code=self.tree.root_node.code,
            parent_node_year=self.tree.root_node.year,
            child_node_code=self.tree.root_node.children_as_nodes[0].code,
            child_node_year=self.tree.root_node.children_as_nodes[0].year,
            link_type=LinkTypes.REFERENCE.name,
        )
        bulk_update_cmd = BulkUpdateLinkCommand(
            working_tree_code=self.tree.root_node.code,
            working_tree_year=self.tree.root_node.year,
            update_link_cmds=[update_link_cmd]
        )

        with self.assertRaises(BulkUpdateLinkException) as e:
            bulk_update_link_service.bulk_update_and_postpone_links(
                bulk_update_cmd,
                self.fake_program_tree_repository,
                ReportRepository()
            )

        self.assertIsInstance(
            next(iter(e.exception.exceptions[update_link_cmd].exceptions)),
            exception.MinimumChildTypesNotRespectedException
        )

    def test_postpone_link_with_consistency_errors(self, mock_calendar):
        self.tree.authorized_relationships.update(
            TrainingType.BACHELOR,
            GroupType.COMMON_CORE,
            max_count_authorized=1,
            min_count_authorized=1,
        )
        tree_next_year = ProgramTreeBuilder().copy_to_next_year(self.tree, self.fake_program_tree_repository)
        self.fake_program_tree_repository.create(tree_next_year)

        common_core_node = self.tree.root_node.children_as_nodes[0]
        update_link_cmd = UpdateLinkCommandFactory(
            parent_node_code=self.tree.root_node.code,
            parent_node_year=self.tree.root_node.year,
            child_node_code=common_core_node.code,
            child_node_year=common_core_node.year,
            is_mandatory=False,
            block="1234",
            comment="test postpone conflict",
            comment_english="test postpone conflict",
            relative_credits=12,
        )
        bulk_update_cmd = BulkUpdateLinkCommand(
            working_tree_code=self.tree.root_node.code,
            working_tree_year=self.tree.root_node.year,
            update_link_cmds=[update_link_cmd]
        )

        bulk_update_link_service.bulk_update_and_postpone_links(
            bulk_update_cmd,
            self.fake_program_tree_repository,
            ReportRepository()
        )

        trees_through_years = self.fake_program_tree_repository.search(code=self.tree.entity_id.code)
        trees_in_future = SearchProgramTreesInFuture.search(self.tree.entity_id, trees_through_years)

        self.assertListEqual(trees_in_future, [tree_next_year])

        conflict_report = ReportRepository().get(ReportIdentity(bulk_update_cmd.transaction_id))
        self.assertTrue(isinstance(conflict_report.warnings[0], CannotPostponeLinkToNextYearAsConsistencyError))
        persisted_tree_next_year = trees_in_future[0]
        link_with_common_core_next_year = persisted_tree_next_year.root_node.children[0]

        self.assertNotEqual(link_with_common_core_next_year.is_mandatory, update_link_cmd.is_mandatory)
        self.assertNotEqual(link_with_common_core_next_year.block, update_link_cmd.block)
        self.assertNotEqual(link_with_common_core_next_year.comment, update_link_cmd.comment)
        self.assertNotEqual(link_with_common_core_next_year.comment_english, update_link_cmd.comment_english)
        self.assertNotEqual(link_with_common_core_next_year.relative_credits, update_link_cmd.relative_credits)
