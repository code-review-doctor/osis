##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from unittest import mock, skip

import attr

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.authorized_relationship import AuthorizedRelationshipObject
from base.models.enums.education_group_types import TrainingType, GroupType, MiniTrainingType
from base.models.enums.link_type import LinkTypes
from program_management.ddd import command
from program_management.ddd.domain import exception
from program_management.ddd.domain.link import LinkIdentity
from program_management.ddd.domain.program_tree import build_path
from program_management.ddd.service.read import get_program_tree_version_service
from program_management.ddd.service.write import paste_element_service
from program_management.models.enums.node_type import NodeType
from program_management.tests.ddd.factories.commands.paste_element_command import PasteElementCommandFactory
from program_management.tests.ddd.factories.domain.program_tree.MASTER_2M import ProgramTree2MFactory
from program_management.tests.ddd.factories.domain.program_tree_version.mini_training.MINECON import MINECONFactory
from program_management.tests.ddd.factories.domain.program_tree_version.training.OSIS1BA import OSIS1BAFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory
from program_management.tests.ddd.factories.program_tree import tree_builder
from program_management.tests.ddd.factories.program_tree_version import StandardProgramTreeVersionFactory
from program_management.tests.ddd.factories.repository.fake import get_fake_program_tree_repository, \
    get_fake_node_repository, get_fake_program_tree_version_repository
from testing.testcases import DDDTestCase


class TestPasteLearningUnitNodeService(DDDTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.tree_version = OSIS1BAFactory()
        self.tree = self.tree_version.tree

        self.learning_unit_node = NodeLearningUnitYearFactory(year=self.tree.root_node.year, persist=True)
        self.mini_training_version = MINECONFactory()

        path = build_path(
            self.tree.root_node,
            self.tree.get_node_by_code_and_year("LOSIS101T", self.tree.root_node.year),
            self.tree.get_node_by_code_and_year("LOSIS102R", self.tree.root_node.year),
        )

        self.cmd = command.PasteElementCommand(
            node_to_paste_code=self.learning_unit_node.code,
            node_to_paste_year=self.learning_unit_node.year,
            path_where_to_paste=path,
            access_condition=True,
            is_mandatory=True,
            block="123",
            link_type=None,
            comment=None,
            comment_english=None,
            relative_credits=None
        )

    def test_cannot_paste_node_to_learning_unit_node(self):
        path = build_path(
            self.tree.root_node,
            self.tree.get_node_by_code_and_year("LOSIS101T", self.tree.root_node.year),
            self.tree.get_node_by_code_and_year("LOSIS102R", self.tree.root_node.year),
            self.tree.get_node_by_code_and_year("LDROI1001", self.tree.root_node.year),
        )
        cmd = attr.evolve(self.cmd, path_where_to_paste=path)

        with self.assertRaises(MultipleBusinessExceptions):
            paste_element_service.paste_element(cmd)

    def test_block_should_be_a_sequence_of_increasing_digit_comprised_between_1_and_6(self):
        cmd = attr.evolve(self.cmd, block="1298")

        with self.assertRaises(MultipleBusinessExceptions):
            paste_element_service.paste_element(cmd)

    def test_cannot_create_a_reference_link_with_a_learning_unit_as_child(self):
        cmd = attr.evolve(self.cmd, link_type=LinkTypes.REFERENCE.name)

        with self.assertRaises(MultipleBusinessExceptions):
            paste_element_service.paste_element(cmd)

    def test_cannot_paste_learning_unit_to_node_who_do_not_allow_learning_units_as_children(self):
        path = build_path(self.tree.root_node)
        cmd = attr.evolve(self.cmd, path_where_to_paste=path)

        with self.assertRaises(MultipleBusinessExceptions):
            paste_element_service.paste_element(cmd)

    def test_cannot_paste_group_year_node_to_node_who_do_not_allow_the_node_type(self):
        path = build_path(self.tree.root_node)
        cmd = attr.evolve(
            self.cmd,
            path_where_to_paste=path,
            node_to_paste_code=self.mini_training_version.tree.root_node.code
        )

        with self.assertRaises(MultipleBusinessExceptions):
            paste_element_service.paste_element(cmd)

    def test_cannot_paste_group_year_node_with_year_different_than_the_tree(self):
        node_to_paste = NodeGroupYearFactory(
            node_type=GroupType.SUB_GROUP,
            year=self.tree.root_node.year - 1,
            persist=True
        )
        cmd = attr.evolve(self.cmd, node_to_paste_code=node_to_paste.code, node_to_paste_year=node_to_paste.year)

        with self.assertRaises(MultipleBusinessExceptions):
            paste_element_service.paste_element(cmd)

    def test_cannot_paste_a_node_if_parent_has_reached_its_maximum_children_allowed_for_this_type(self):
        node_to_paste = NodeGroupYearFactory(
            node_type=GroupType.COMMON_CORE,
            year=self.tree.root_node.year,
            persist=True
        )

        cmd = attr.evolve(
            self.cmd,
            node_to_paste_code=node_to_paste.code,
            node_to_paste_year=node_to_paste.year,
            path_where_to_paste=build_path(self.tree.root_node)
        )

        with self.assertRaises(MultipleBusinessExceptions):
            paste_element_service.paste_element(cmd)

    def test_cannot_have_node_containing_itself(self):
        cmd = attr.evolve(self.cmd, node_to_paste_code="LOSIS102R")

        with self.assertRaises(MultipleBusinessExceptions):
            paste_element_service.paste_element(cmd)

    def test_cannot_have_multiple_occurrences_of_same_child(self):
        cmd = attr.evolve(self.cmd, node_to_paste_code="LDROI1001")

        with self.assertRaises(MultipleBusinessExceptions):
            paste_element_service.paste_element(cmd)

    def test_should_return_link_identity_of_link_newly_created(self):
        result = paste_element_service.paste_element(self.cmd)

        expected_identity = LinkIdentity(
            parent_year=self.tree.root_node.year,
            parent_code="LOSIS102R",
            child_year=self.tree.root_node.year,
            child_code=self.learning_unit_node.code
        )

        self.assertEqual(expected_identity, result)

    def test_should_persist_tree_with_new_link_created(self):
        link_identity = paste_element_service.paste_element(self.cmd)

        tree_version = self.reload_tree_version()

        tree_link_identities = [link.entity_id for link in tree_version.get_tree().get_all_links()]
        self.assertIn(link_identity, tree_link_identities)

    def test_should_set_is_mandatory_as_false_when_parent_is_a_list_minor_or_major_or_option(self):
        path = build_path(
            self.tree.root_node,
            self.tree.get_node_by_code_and_year("LOSIS101G", self.tree.root_node.year),
        )

        cmd = attr.evolve(
            self.cmd,
            path_where_to_paste=path,
            node_to_paste_code=self.mini_training_version.tree.root_node.code,
            is_mandatory=True
        )

        link_identity = paste_element_service.paste_element(cmd)
        tree_version = self.reload_tree_version()
        link = tree_version.get_tree().get_link_by_identity(link_identity)

        self.assertFalse(link.is_mandatory)

    def test_should_set_link_type_as_reference_when_parent_is_a_list_minor_or_major_and_child_is_minor_or_major(self):
        path = build_path(
            self.tree.root_node,
            self.tree.get_node_by_code_and_year("LOSIS101G", self.tree.root_node.year),
        )

        cmd = attr.evolve(
            self.cmd,
            path_where_to_paste=path,
            node_to_paste_code=self.mini_training_version.tree.root_node.code,
            link_type=None
        )

        link_identity = paste_element_service.paste_element(cmd)
        tree_version = self.reload_tree_version()
        link = tree_version.get_tree().get_link_by_identity(link_identity)

        self.assertTrue(link.is_reference())

    def test_should_be_able_to_paste_a_list_minor_major_to_a_list_minor_major(self):
        node_types = [GroupType.MINOR_LIST_CHOICE, GroupType.MAJOR_LIST_CHOICE]
        path = build_path(
            self.tree.root_node,
            self.tree.get_node_by_code_and_year("LOSIS101G", self.tree.root_node.year),
        )
        for node_type in node_types:
            with self.subTest(node_type=node_type):
                node_to_paste = NodeGroupYearFactory(node_type=node_type, year=self.tree.root_node.year, persist=True)
                cmd = attr.evolve(
                    self.cmd,
                    path_where_to_paste=path,
                    node_to_paste_code=node_to_paste.code,
                    node_to_paste_year=node_to_paste.year
                )
                self.assertTrue(paste_element_service.paste_element(cmd))

    @skip("This test should be incorporated in group")
    def test_cannot_paste_if_do_not_allow_referenced_children(self):
        tree_data = {
            "node_type": GroupType.SUB_GROUP,
            "year": 2020,
            "end_year": 2025,
            "node_id": 100,
            "children": [
                {
                    "node_type": NodeType.LEARNING_UNIT,
                    "year": 2020,
                    "end_date": 2025,
                    "node_id": 101,
                }
            ]
        }
        tree_to_paste = tree_builder(tree_data)
        self.fake_program_tree_repository._trees.append(tree_to_paste)

        invalid_command = PasteElementCommandFactory(
            node_to_paste_code=tree_to_paste.root_node.code,
            node_to_paste_year=tree_to_paste.root_node.year,
            path_where_to_paste="1|21",
            link_type=LinkTypes.REFERENCE.name
        )

        self.assertRaisesBusinessException(
            exception.ChildTypeNotAuthorizedException,
            paste_element_service.paste_element,
            invalid_command
        )

    def reload_tree_version(self):
        tree_version = get_program_tree_version_service.get_program_tree_version(
            command.GetProgramTreeVersionCommand(
                year=self.tree_version.entity_id.year,
                acronym=self.tree_version.entity_id.offer_acronym,
                version_name=self.tree_version.entity_id.version_name,
                transition_name=self.tree_version.entity_id.transition_name,
            )
        )
        return tree_version


class TestPasteGroupNodeService(DDDTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.tree = ProgramTreeBachelorFactory(2020, 2025)

        tree_to_paste_data = {
            "node_type": MiniTrainingType.OPTION,
            "year": 2020
        }
        self.tree_to_paste = tree_builder(tree_to_paste_data)
        self.node_to_paste = self.tree_to_paste.root_node

        self.fake_program_tree_repository = get_fake_program_tree_repository([self.tree, self.tree_to_paste])
        self.tree_version = StandardProgramTreeVersionFactory(
            tree=self.tree,
            program_tree_repository=self.fake_program_tree_repository
        )
        self.tree_version_to_paste = StandardProgramTreeVersionFactory(
            tree=self.tree_to_paste,
            program_tree_repository=self.fake_program_tree_repository
        )
        self.mock_repo(
            "program_management.ddd.repositories.program_tree.ProgramTreeRepository",
            self.fake_program_tree_repository
        )

        self.fake_tree_version_repository = get_fake_program_tree_version_repository(
            [self.tree_version, self.tree_version_to_paste]
        )
        self.mock_repo(
            "program_management.ddd.repositories.program_tree_version.ProgramTreeVersionRepository",
            self.fake_tree_version_repository
        )

        self.fake_node_repository = get_fake_node_repository([self.node_to_paste])
        self.mock_repo(
            "program_management.ddd.repositories.node.NodeRepository",
            self.fake_node_repository
        )

        self.mocked_get_from_element_id = self.mock_get_program_tree_identity_from_element_id()
        self.mocked_get_from_element_id.return_value = self.tree.entity_id

    def mock_get_program_tree_identity_from_element_id(self):
        pacher = mock.patch(
            "program_management.ddd.domain.service."
            "identity_search.ProgramTreeIdentitySearch.get_from_element_id"
        )
        mocked_method = pacher.start()
        self.addCleanup(pacher.stop)
        return mocked_method

    def test_cannot_paste_if_reference_link_and_referenced_children_are_not_allowed(self):
        tree_to_paste = tree_builder(
            {
                "node_type": GroupType.MINOR_LIST_CHOICE,
                "year": 2020,
                "children": [
                    {"node_type": NodeType.LEARNING_UNIT},
                    {"node_type": GroupType.SUB_GROUP, "year": 2020}
                ]
            }
        )
        self.fake_program_tree_repository._trees.append(tree_to_paste)
        self.fake_node_repository._nodes.append(tree_to_paste.root_node)
        self.fake_tree_version_repository._trees_version.append(
            StandardProgramTreeVersionFactory(
                tree=tree_to_paste,
                program_tree_repository=self.fake_program_tree_repository,
            )
        )

        invalid_command = PasteElementCommandFactory(
            node_to_paste_code=tree_to_paste.root_node.code,
            node_to_paste_year=tree_to_paste.root_node.year,
            path_where_to_paste="1",
            link_type=LinkTypes.REFERENCE.name
        )

        self.assertRaisesBusinessException(
            exception.ChildTypeNotAuthorizedException,
            paste_element_service.paste_element,
            invalid_command
        )

    def test_cannot_paste_list_finalities_inside_list_finalities_if_max_finalities_is_surpassed(self):
        tree_to_paste_data = {
            "node_type": GroupType.FINALITY_120_LIST_CHOICE,
            "year": 2020,
            "children": [
                {
                    "node_type": TrainingType.MASTER_MD_120,
                    "year": 2020,
                    "end_year": 2025
                },
            ]
        }

        tree = ProgramTree2MFactory(2020, 2025)
        tree_to_paste = tree_builder(tree_to_paste_data)

        self.fake_program_tree_repository._trees.append(tree_to_paste)
        self.fake_program_tree_repository._trees.append(tree)
        self.fake_tree_version_repository._trees_version.append(
            StandardProgramTreeVersionFactory(
                tree=tree_to_paste,
                program_tree_repository=self.fake_program_tree_repository,
            )
        )
        self.fake_tree_version_repository._trees_version.append(
            StandardProgramTreeVersionFactory(
                tree=tree,
                program_tree_repository=self.fake_program_tree_repository,
            )
        )
        tree.authorized_relationships.update(
            parent_type=GroupType.FINALITY_120_LIST_CHOICE,
            child_type=TrainingType.MASTER_MD_120,
            min_count_authorized=1,
            max_count_authorized=1
        )
        tree.authorized_relationships.authorized_relationships.append(
            AuthorizedRelationshipObject(
                parent_type=GroupType.FINALITY_120_LIST_CHOICE,
                child_type=GroupType.FINALITY_120_LIST_CHOICE,
                min_count_authorized=0,
                max_count_authorized=None
            )
        )

        self.mocked_get_from_element_id.return_value = tree.entity_id

        invalid_command = PasteElementCommandFactory(
            node_to_paste_code=tree_to_paste.root_node.code,
            node_to_paste_year=tree_to_paste.root_node.year,
            path_where_to_paste="1|22",
        )

        self.assertRaisesBusinessException(
            exception.MaximumChildTypesReachedException,
            paste_element_service.paste_element,
            invalid_command
        )
