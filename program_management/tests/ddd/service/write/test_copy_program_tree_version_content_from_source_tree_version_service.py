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
import attr
import mock

from base.tests.factories.validation_rule import ValidationRuleFactory
from program_management.ddd.command import CopyProgramTreeVersionContentFromSourceTreeVersionCommand
from program_management.ddd.domain.exception import ProgramTreeNonEmpty, InvalidTreeVersionToFillFrom
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion, ProgramTreeVersionIdentity
from program_management.ddd.service.write.copy_program_tree_version_content_from_source_tree_version_service import \
    fill_program_tree_version_content_from_source
from program_management.tests.ddd.factories.domain.program_tree.BACHELOR_1BA import ProgramTreeBachelorFactory
from program_management.tests.ddd.factories.domain.program_tree.MASTER_2M import ProgramTree2MFactory
from program_management.tests.ddd.factories.node import NodeFactory, NodeGroupYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.ddd.factories.program_tree_version import StandardProgramTreeVersionFactory, \
    SpecificProgramTreeVersionFactory, ProgramTreeVersionFactory
from program_management.tests.ddd.factories.repository.fake import get_fake_program_tree_version_repository, \
    get_fake_program_tree_repository
from testing.mocks import MockPatcherMixin
from testing.testcases import DDDTestCase


# TODO rename to fill content
class TestCopyProgramTreeVersionContentFromSourceTreeVersion(MockPatcherMixin, DDDTestCase):
    def setUp(self) -> None:
        self.tree_version_from = StandardProgramTreeVersionFactory(
            tree=ProgramTreeBachelorFactory(current_year=2020, end_year=2021)
        )
        self.tree_version_to_fill = StandardProgramTreeVersionFactory(
            tree__root_node__title=self.tree_version_from.entity_id.offer_acronym,
            tree__root_node__year=2021
        )
        self.transition_tree_version_to_fill = StandardProgramTreeVersionFactory(
            transition=True,
            tree__root_node__title=self.tree_version_from.entity_id.offer_acronym,
            tree__root_node__year=2021
        )
        self.cmd = self._generate_cmd(self.tree_version_from, self.tree_version_to_fill)
        self.cmd_for_transition = self._generate_cmd(self.tree_version_from, self.transition_tree_version_to_fill)

        self.fake_program_tree_version_repository = get_fake_program_tree_version_repository(
            [self.tree_version_from, self.transition_tree_version_to_fill, self.tree_version_to_fill]
        )
        self.mock_repo(
            "program_management.ddd.repositories.program_tree_version.ProgramTreeVersionRepository",
            self.fake_program_tree_version_repository
        )
        self.fake_program_tree_repository = get_fake_program_tree_repository(
            [self.tree_version_from.tree, self.transition_tree_version_to_fill.tree, self.tree_version_to_fill.tree]
        )
        self.mock_repo(
            "program_management.ddd.repositories.program_tree.ProgramTreeRepository",
            self.fake_program_tree_repository
        )
        self.mock_generate_code()

    def mock_generate_code(self):
        patcher = mock.patch(
            "program_management.ddd.domain.node.GenerateNodeCode.generate_from_parent_node",
            side_effect=lambda parent_node, **kwargs: "T" + parent_node.code
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_should_return_identify_of_tree_version_that_has_its_content_filled(self):
        result = fill_program_tree_version_content_from_source(self.cmd)
        expected_identity = self.tree_version_to_fill.entity_id
        self.assertEqual(expected_identity, result)

    def test_should_persist_filled_content(self):
        fill_program_tree_version_content_from_source(self.cmd)
        self.assertCountEqual(
            [(node.code, node.year) for node in self.tree_version_from.tree.get_all_nodes() - {self.tree_version_from.tree.root_node}],
            [(node.code, node.year-1) for node in self.tree_version_to_fill.tree.get_all_nodes() - {self.tree_version_to_fill.tree.root_node}]
        )

    def test_should_omit_nodes_that_have_end_year_inferior_to_tree_to_fill(self):
        self.tree_version_from.tree.get_node("1|22|32").end_date = 2020
        fill_program_tree_version_content_from_source(self.cmd_for_transition)

        self.assertTrue(
            len(self.tree_version_from.tree.get_all_nodes()) > len(self.transition_tree_version_to_fill.tree.get_all_nodes())
        )

    def test_should_raise_exception_when_tree_to_fill_is_not_empty(self):
        fill_program_tree_version_content_from_source(self.cmd_for_transition)
        self.assertRaisesBusinessException(
            ProgramTreeNonEmpty,
            fill_program_tree_version_content_from_source,
            self.cmd_for_transition
        )

    def test_should_copy_prerequisites_from_tree_to_copy_from_to_tree_to_fill(self):
        fill_program_tree_version_content_from_source(self.cmd)

        self.assertEqual(
            len(self.tree_version_from.tree.prerequisites.prerequisites),
            len(self.tree_version_to_fill.tree.prerequisites.prerequisites)
        )

    # TODO :: use property to generate
    def test_can_only_fill_program_specific_official_from_its_last_year_self(self):
        tree_to_fill_from = ProgramTreeVersionFactory()
        tree_to_fill = SpecificProgramTreeVersionFactory()
        self.fake_program_tree_version_repository.root_entities.append(tree_to_fill_from)
        self.fake_program_tree_version_repository.root_entities.append(tree_to_fill)

        cmd = self._generate_cmd(tree_to_fill_from, tree_to_fill)

        self.assertRaisesBusinessException(
            InvalidTreeVersionToFillFrom,
            fill_program_tree_version_content_from_source,
            cmd
        )

    # TODO :: use property to generate
    def test_can_only_fill_standard_transition_from_its_last_year_self_or_standard_or_last_year_standard(self):
        tree_to_fill_from = ProgramTreeVersionFactory()
        tree_to_fill = StandardProgramTreeVersionFactory(transition=True)
        self.fake_program_tree_version_repository.root_entities.append(tree_to_fill_from)
        self.fake_program_tree_version_repository.root_entities.append(tree_to_fill)

        cmd = self._generate_cmd(tree_to_fill_from, tree_to_fill)

        self.assertRaisesBusinessException(
            InvalidTreeVersionToFillFrom,
            fill_program_tree_version_content_from_source,
            cmd
        )

    # TODO :: use property to generate
    def test_can_only_fill_specific_transition_from_its_last_year_self_or_specific_or_last_year_specific(self):
        tree_to_fill_from = ProgramTreeVersionFactory()
        tree_to_fill = SpecificProgramTreeVersionFactory(transition=True)
        self.fake_program_tree_version_repository.root_entities.append(tree_to_fill_from)
        self.fake_program_tree_version_repository.root_entities.append(tree_to_fill)

        cmd = self._generate_cmd(tree_to_fill_from, tree_to_fill)

        self.assertRaisesBusinessException(
            InvalidTreeVersionToFillFrom,
            fill_program_tree_version_content_from_source,
            cmd
        )

    def test_when_transition_should_rename_group_code_with_replacing_first_letter_by_T(self):
        fill_program_tree_version_content_from_source(self.cmd_for_transition)

        groups = [node for node in self.transition_tree_version_to_fill.tree.get_all_nodes() if node.is_group()]
        self.assertTrue(
            all(
                [group.code.startswith("T") for group in groups]
            )
        )

    @mock.patch(
        "program_management.ddd.domain.service.validation_rule.FieldValidationRule.get",
        side_effect=lambda *args, **kwargs: ValidationRuleFactory(initial_value=5)
    )
    @mock.patch(
        "program_management.ddd.repositories.node.NodeRepository.get",
        side_effect=lambda *args, **kwargs: NodeGroupYearFactory()
    )
    def test_when_transition_should_create_associated_training(self, mock_field_validation, mock_node_get):
        tree_version_from = StandardProgramTreeVersionFactory(
            tree=ProgramTree2MFactory(current_year=2021, end_year=2021)
        )
        tree_finality = StandardProgramTreeVersionFactory(
            tree=ProgramTreeFactory(
                root_node=tree_version_from.tree.get_node("1|22|33")
            )
        )
        tree_version_to = StandardProgramTreeVersionFactory(
            transition=True,
            tree__root_node__title=tree_version_from.entity_id.offer_acronym,
            tree__root_node__year=2021
        )
        tree_version_to.entity_id = attr.evolve(
            tree_version_to.entity_id,
            transition_name=tree_version_to.transition_name
        )
        tree_version_to.entity_identity = tree_version_to.entity_id

        self.fake_program_tree_version_repository.root_entities.extend([tree_version_from, tree_version_to, tree_finality])
        self.fake_program_tree_repository.root_entities.extend([tree_version_from.tree, tree_version_to.tree, tree_finality.tree])

        cmd = self._generate_cmd(tree_version_from, tree_version_to)
        fill_program_tree_version_content_from_source(cmd)

        master_2md_node = tree_version_from.tree.get_node("1|22|33")
        self.assertTrue(
            self.fake_program_tree_version_repository.get(
                ProgramTreeVersionIdentity(
                    offer_acronym=master_2md_node.title,
                    year=master_2md_node.year,
                    version_name=tree_version_to.version_name,
                    transition_name=tree_version_to.transition_name
                )
            )
        )

    def _generate_cmd(
            self,
            tree_from: 'ProgramTreeVersion',
            tree_to: 'ProgramTreeVersion',
    ) -> 'CopyProgramTreeVersionContentFromSourceTreeVersionCommand':
        return CopyProgramTreeVersionContentFromSourceTreeVersionCommand(
            from_year=tree_from.entity_id.year,
            from_offer_acronym=tree_from.entity_id.offer_acronym,
            from_version_name=tree_from.entity_id.version_name,
            from_transition_name=tree_from.entity_id.transition_name,
            to_year=tree_to.entity_id.year,
            to_offer_acronym=tree_to.entity_id.offer_acronym,
            to_version_name=tree_to.entity_id.version_name,
            to_transition_name=tree_to.entity_id.transition_name
        )
