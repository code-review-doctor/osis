##############################################################################
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import copy

from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.utils.translation import gettext_lazy as _

from base.models.enums.prerequisite_operator import OR
from program_management.business.excel import HeaderLine, OfficialTextLine, LearningUnitYearLine, PrerequisiteItemLine
from program_management.business.excel import _build_excel_lines
from program_management.tests.ddd.factories.domain.prerequisite.prerequisite import PrerequisitesFactory
from program_management.tests.ddd.factories.domain.program_tree.LDROI200M_DROI2M import ProgramTreeDROI2MFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory


class TestGeneratePrerequisitesWorkbook(SimpleTestCase):

    def setUp(self):
        self.year = 2019
        self.tree_droi2m = ProgramTreeDROI2MFactory(root_node__year=self.year)
        self.common_core = self.tree_droi2m.get_node_by_code_and_year("LDROI220T", self.year)

    def test_header_lines_offer(self):
        expected_first_line = HeaderLine(egy_acronym=self.tree_droi2m.root_node.title,
                                         egy_title=self.tree_droi2m.root_node.offer_title_fr,
                                         code_header=_('Code'),
                                         title_header=_('Title'),
                                         credits_header=_('Cred. rel./abs.'),
                                         block_header=_('Block'),
                                         mandatory_header=_('Mandatory')
                                         )
        expected_second_line = OfficialTextLine(text=_("Official"))

        headers = _build_excel_lines(self.tree_droi2m)
        self.assertEqual(expected_first_line, headers[0])
        self.assertEqual(expected_second_line, headers[1])

    def test_header_lines_group(self):
        group_as_program_tree = ProgramTreeFactory(root_node=self.common_core)
        expected_first_line = HeaderLine(egy_acronym=group_as_program_tree.root_node.title,
                                         egy_title=group_as_program_tree.root_node.group_title_fr,
                                         code_header=_('Code'),
                                         title_header=_('Title'),
                                         credits_header=_('Cred. rel./abs.'),
                                         block_header=_('Block'),
                                         mandatory_header=_('Mandatory')
                                         )

        headers = _build_excel_lines(group_as_program_tree)
        self.assertEqual(expected_first_line, headers[0])

    @override_settings(LANGUAGES=[('en', 'English'), ], LANGUAGE_CODE='en')
    def test_when_learning_unit_year_has_one_prerequisite(self):
        tree = copy.deepcopy(self.tree_droi2m)
        node_has_prerequisite = tree.get_node_by_code_and_year(code="LDROP2011", year=self.year)
        node_is_prerequisite = tree.get_node_by_code_and_year(code="LDROI2101", year=self.year)
        link_with_node_is_prerequisite = tree.get_link(self.common_core, node_is_prerequisite)
        PrerequisitesFactory.produce_inside_tree(
            context_tree=tree,
            node_having_prerequisite=node_has_prerequisite.entity_id,
            nodes_that_are_prequisites=[node_is_prerequisite.entity_id]
        )

        content = _build_excel_lines(tree)
        learning_unit_year_line = content[2]
        prerequisite_item_line = content[3]

        expected_learning_unit_year_line = LearningUnitYearLine(
            luy_acronym=node_has_prerequisite.code,
            luy_title=node_has_prerequisite.full_title_en,
            empty_col1='',
            empty_col2='',
            credits=link_with_node_is_prerequisite.relative_credits_repr,
            blocks=str(link_with_node_is_prerequisite.block) if link_with_node_is_prerequisite.block else '',
            mandatory_status=_("Yes") if link_with_node_is_prerequisite.is_mandatory else _("No")
        )
        expected_prerequisite_item_line = PrerequisiteItemLine(
            text='{} :'.format(_('has as prerequisite')),
            operator=None,
            luy_acronym=node_is_prerequisite.code,
            luy_title=node_is_prerequisite.title,
            credits=link_with_node_is_prerequisite.relative_credits_repr,
            block=str(link_with_node_is_prerequisite.block) if link_with_node_is_prerequisite.block else '',
            mandatory=_("Yes") if link_with_node_is_prerequisite.is_mandatory else _("No")
        )
        self.assertEqual(expected_learning_unit_year_line, learning_unit_year_line)
        self.assertEqual(expected_prerequisite_item_line, prerequisite_item_line)

    @override_settings(LANGUAGES=[('en', 'English'), ], LANGUAGE_CODE='en')
    def test_when_learning_unit_year_has_multiple_prerequisites(self):
        tree = copy.deepcopy(self.tree_droi2m)
        node_has_prerequisite = tree.get_node_by_code_and_year(code="LDROP2011", year=self.year)
        node_is_prerequisite1 = tree.get_node_by_code_and_year(code="LDROI2101", year=self.year)
        node_is_prerequisite2 = tree.get_node_by_code_and_year(code="LDROI2102", year=self.year)
        link_with_node_is_prerequisite1 = tree.get_link(self.common_core, node_is_prerequisite1)
        link_with_node_is_prerequisite2 = tree.get_link(self.common_core, node_is_prerequisite2)

        PrerequisitesFactory.produce_inside_tree(
            context_tree=tree,
            node_having_prerequisite=node_has_prerequisite.entity_id,
            nodes_that_are_prequisites=[node_is_prerequisite1.entity_id, node_is_prerequisite2.entity_id],
            operator=OR
        )

        content = _build_excel_lines(tree)
        learning_unit_year_line = content[2]

        expected_learning_unit_year_line = LearningUnitYearLine(
            luy_acronym=node_has_prerequisite.code,
            luy_title=node_has_prerequisite.full_title_en,
            empty_col1='',
            empty_col2='',
            credits=self._expected_credits_repr(link_with_node_is_prerequisite1, link_with_node_is_prerequisite2),
            blocks=self._expected_blocks_repr(
                link_with_node_is_prerequisite1.block,
                link_with_node_is_prerequisite2.block
            ),
            mandatory_status=self._expected_mandatory_status(
                link_with_node_is_prerequisite1.is_mandatory,
                link_with_node_is_prerequisite2.is_mandatory
            ),
        )
        self.assertEqual(expected_learning_unit_year_line, learning_unit_year_line)

        prerequisite_item_line_1 = content[3]
        expected_prerequisite_item_line1 = PrerequisiteItemLine(
            text='{} :'.format(_('has as prerequisite')),
            operator=None,
            luy_acronym="({}".format(node_is_prerequisite1.code),
            luy_title=node_is_prerequisite1.title,
            credits=link_with_node_is_prerequisite1.relative_credits_repr,
            block=str(link_with_node_is_prerequisite1.block) if link_with_node_is_prerequisite1.block else '',
            mandatory=_("Yes") if link_with_node_is_prerequisite1.is_mandatory else _("No")
        )
        self.assertEqual(prerequisite_item_line_1, expected_prerequisite_item_line1)

        prerequisite_item_line_2 = content[4]

        expected_prerequisite_item_line2 = PrerequisiteItemLine(
            text=None,
            operator=_(OR),
            luy_acronym="{})".format(node_is_prerequisite2.code),
            luy_title=node_is_prerequisite2.title,
            credits=link_with_node_is_prerequisite2.relative_credits_repr,
            block=str(link_with_node_is_prerequisite2.block) if link_with_node_is_prerequisite2.block else '',
            mandatory=_("Yes") if link_with_node_is_prerequisite2.is_mandatory else _("No")
        )
        self.assertEqual(prerequisite_item_line_2, expected_prerequisite_item_line2)

    def _expected_blocks_repr(self, block1: str, block2: str):
        blocks = set()
        if block1:
            blocks.add(str(block1))
        if block2:
            blocks.add(str(block2))
        return " ; ".join(sorted(blocks))

    def _expected_credits_repr(self, link_with_node_is_prerequisite1, link_with_node_is_prerequisite2):
        credits = set()
        credits.add(link_with_node_is_prerequisite1.relative_credits_repr)
        credits.add(link_with_node_is_prerequisite2.relative_credits_repr)
        return " ; ".join(sorted(credits))

    def _expected_mandatory_status(self, is_mandatory1: bool, is_mandatory2: bool):
        mandatory_status = set()
        mandatory_status.add(str(_("Yes")) if is_mandatory1 else str(_("No")))
        mandatory_status.add(str(_("Yes")) if is_mandatory2 else str(_("No")))
        return " ; ".join(sorted(mandatory_status))
