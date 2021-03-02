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
import mock

from program_management.ddd.command import CopyProgramTreeVersionContentFromSourceTreeVersionCommand
from program_management.ddd.domain.academic_year import AcademicYear
from program_management.ddd.domain.exception import InvalidTreeVersionToFillTo, InvalidTreeVersionToFillFrom, \
    ProgramTreeNonEmpty
from program_management.ddd.domain.program_tree_version import ProgramTreeVersion
from program_management.ddd.service.write.copy_program_tree_version_content_from_source_tree_version_service import \
    fill_program_tree_version_content_from_source
from program_management.tests.ddd.factories.domain.program_tree.BACHELOR_1BA import ProgramTreeBachelorFactory
from program_management.tests.ddd.factories.program_tree_version import StandardProgramTreeVersionFactory, \
    SpecificProgramTreeVersionFactory
from testing.testcases import DDDTestCase

CURRENT_ACADEMIC_YEAR_YEAR = 2021
NEXT_ACADEMIC_YEAR_YEAR = 2022


class TestFillProgramTreeVersionContentFromSourceTreeVersion(DDDTestCase):
    def setUp(self) -> None:
        self._init_fake_repos()

        self.tree_version_from = SpecificProgramTreeVersionFactory(
            tree=ProgramTreeBachelorFactory(current_year=CURRENT_ACADEMIC_YEAR_YEAR, end_year=NEXT_ACADEMIC_YEAR_YEAR)
        )
        self.tree_version_to_fill = SpecificProgramTreeVersionFactory(
            tree__root_node__code=self.tree_version_from.tree.root_node.code,
            tree__root_node__title=self.tree_version_from.entity_id.offer_acronym,
            tree__root_node__year=NEXT_ACADEMIC_YEAR_YEAR
        )
        self.cmd = self._generate_cmd(self.tree_version_from, self.tree_version_to_fill)

        self.fake_program_tree_version_repository.root_entities.extend(
            [self.tree_version_from, self.tree_version_to_fill]
        )
        self.fake_program_tree_repository.root_entities.extend(
            [self.tree_version_from.tree, self.tree_version_to_fill.tree]
        )

        self.mock_generate_code()
        self.mock_get_current_academic_year()

    def mock_generate_code(self):
        patcher = mock.patch(
            "program_management.ddd.domain.node.GenerateNodeCode.generate_from_parent_node",
            side_effect=lambda parent_node, **kwargs: "T" + parent_node.code
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def mock_get_current_academic_year(self):
        patcher = mock.patch(
            "program_management.ddd.domain.service.get_academic_year.GetAcademicYear.get_next_academic_year",
            side_effect=lambda *args, **kwargs: AcademicYear(NEXT_ACADEMIC_YEAR_YEAR)
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_can_only_fill_content_of_next_academic_year(self):
        tree_version_to_fill = StandardProgramTreeVersionFactory(
            tree__root_node__title=self.tree_version_from.entity_id.offer_acronym,
            tree__root_node__year=CURRENT_ACADEMIC_YEAR_YEAR
        )
        self.fake_program_tree_version_repository.root_entities.append(tree_version_to_fill)
        cmd = self._generate_cmd(self.tree_version_from, tree_version_to_fill)

        self.assertRaisesBusinessException(
            InvalidTreeVersionToFillTo,
            fill_program_tree_version_content_from_source,
            cmd
        )

    def test_if_specific_official_can_only_copy_from_its_previous_year(self):
        tree_version_to_fill_from = SpecificProgramTreeVersionFactory(
            tree__root_node__year=CURRENT_ACADEMIC_YEAR_YEAR - 1
        )
        tree_version_to_fill = SpecificProgramTreeVersionFactory(
            tree__root_node__title=tree_version_to_fill_from.entity_id.offer_acronym,
            tree__root_node__year=NEXT_ACADEMIC_YEAR_YEAR
        )

        self.fake_program_tree_version_repository.root_entities.extend([tree_version_to_fill_from, tree_version_to_fill])
        cmd = self._generate_cmd(tree_version_to_fill_from, tree_version_to_fill)

        self.assertRaisesBusinessException(
            InvalidTreeVersionToFillFrom,
            fill_program_tree_version_content_from_source,
            cmd
        )

    def test_cannot_fill_non_empty_tree(self):
        tree_version_to_fill_to = SpecificProgramTreeVersionFactory(
            tree=ProgramTreeBachelorFactory(
                current_year=NEXT_ACADEMIC_YEAR_YEAR,
                end_year=NEXT_ACADEMIC_YEAR_YEAR
            )
        )
        tree_version_to_fill_from = SpecificProgramTreeVersionFactory(
            tree__root_node__code=tree_version_to_fill_to.tree.root_node.code,
            tree__root_node__year=CURRENT_ACADEMIC_YEAR_YEAR
        )

        self.fake_program_tree_version_repository.root_entities.append(tree_version_to_fill_to)
        self.fake_program_tree_version_repository.root_entities.append(tree_version_to_fill_from)
        cmd = self._generate_cmd(tree_version_to_fill_from, tree_version_to_fill_to)

        self.assertRaisesBusinessException(
            ProgramTreeNonEmpty,
            fill_program_tree_version_content_from_source,
            cmd
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
