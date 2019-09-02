##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from base.business.education_groups.excel import EducationGroupYearLearningUnitsPrerequisitesToExcel
from base.models.enums.prerequisite_operator import AND, OR
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearChildLeafFactory
from base.tests.factories.prerequisite import PrerequisiteFactory


class TestGeneratePrerequisitesWorkbook(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.education_group_year = EducationGroupYearFactory()
        cls.child_leaves = GroupElementYearChildLeafFactory.create_batch(
            6,
            parent=cls.education_group_year
        )
        luy_acronyms = ["LCORS124" + str(i) for i in range(0, len(cls.child_leaves))]
        for node, acronym in zip(cls.child_leaves, luy_acronyms):
            node.child_leaf.acronym = acronym
            node.child_leaf.save()

        cls.luy_children = [child.child_leaf for child in cls.child_leaves]

        PrerequisiteFactory(
            learning_unit_year=cls.luy_children[0],
            education_group_year=cls.education_group_year,
            items__groups=(
                (cls.luy_children[1],),
            )
        )
        PrerequisiteFactory(
            learning_unit_year=cls.luy_children[2],
            education_group_year=cls.education_group_year,
            items__groups=(
                (cls.luy_children[3],),
                (cls.luy_children[4], cls.luy_children[5])
            )
        )

        cls.workbook = EducationGroupYearLearningUnitsPrerequisitesToExcel(cls.education_group_year)._to_workbook()
        cls.sheet = cls.workbook.worksheets[0]

    def test_header_lines(self):
        expected_headers = [
            [self.education_group_year.acronym, self.education_group_year.title],
            [_("Official"), None]
        ]

        headers = [row_to_value(row) for row in self.sheet.iter_rows(range_string="A1:B2")]
        self.assertListEqual(headers, expected_headers)

    def test_when_learning_unit_year_has_one_prerequisite(self):
        expected_content = [
            [self.luy_children[0].acronym, self.luy_children[0].complete_title, None, None, None, None, None],

            [_("has as prerequisite") + " :", '', self.luy_children[1].acronym,
             self.luy_children[1].complete_title_i18n,
             "{} / {}".format(self.child_leaves[1].relative_credits, self.luy_children[1].credits),
             str(self.child_leaves[1].block) if self.child_leaves[1].block else '',
             _("Yes") if self.child_leaves[1].is_mandatory else _("No")]
        ]

        content = [row_to_value(row) for row in self.sheet.iter_rows(range_string="A3:G4")]
        self.assertListEqual(expected_content, content)

    def test_when_learning_unit_year_has_multiple_prerequisites(self):
        expected_content = [
            [self.luy_children[2].acronym, self.luy_children[2].complete_title, None, None, None, None, None],

            [_("has as prerequisite") + " :", '', self.luy_children[3].acronym,
             self.luy_children[3].complete_title_i18n,
             "{} / {}".format(self.child_leaves[3].relative_credits, self.luy_children[3].credits),
             str(self.child_leaves[3].block) if self.child_leaves[3].block else '',
             _("Yes") if self.child_leaves[3].is_mandatory else _("No")],

            ['', _(AND), "(" + self.luy_children[4].acronym, self.luy_children[4].complete_title_i18n,
             "{} / {}".format(self.child_leaves[4].relative_credits, self.luy_children[4].credits),
             str(self.child_leaves[4].block) if self.child_leaves[4].block else '',
             _("Yes") if self.child_leaves[4].is_mandatory else _("No")
             ],

            ['', _(OR), self.luy_children[5].acronym + ")", self.luy_children[5].complete_title_i18n,
             "{} / {}".format(self.child_leaves[5].relative_credits, self.luy_children[5].credits),
             str(self.child_leaves[5].block) if self.child_leaves[5].block else '',
             _("Yes") if self.child_leaves[5].is_mandatory else _("No")
             ]
        ]
        content = [row_to_value(row) for row in self.sheet.iter_rows(range_string="A5:G8")]
        self.assertListEqual(expected_content, content)

    @staticmethod
    def get_luy_line(luy):
        return [luy.acronym, luy.complete_title, None, None, None, None, None]

    @staticmethod
    def get_item_line(luy, grp, operator, first_item=False):
        return [
            (_("has as prerequisite") + " :") if first_item else None,
            operator,
            luy.acronym,
            luy.complete_title_i18n,
            "{} / {}".format(grp.relative_credits, luy.credits),
            str(grp.block),
            _("Yes") if grp.is_mandatory else _("No")]


def row_to_value(sheet_row):
    return [cell.value for cell in sheet_row]
