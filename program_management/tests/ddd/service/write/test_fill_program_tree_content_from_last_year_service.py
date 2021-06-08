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
from django.test import override_settings

from program_management.ddd.command import FillProgramTreeContentFromLastYearCommand
from program_management.ddd.domain.node import factory as node_factory
from program_management.ddd.service.write import fill_program_tree_content_from_last_year_service
from program_management.tests.ddd.factories.domain.program_tree_version.training.OSIS2M import OSIS2MFactory
from testing.testcases import DDDTestCase

PAST_ACADEMIC_YEAR_YEAR = 2020
CURRENT_ACADEMIC_YEAR_YEAR = 2021
NEXT_ACADEMIC_YEAR_YEAR = 2022


@override_settings(YEAR_LIMIT_EDG_MODIFICATION=PAST_ACADEMIC_YEAR_YEAR)
class TestFillProgramTreeContentFromLastYear(DDDTestCase):
    def setUp(self) -> None:
        super().setUp()
        tree_versions = OSIS2MFactory()
        self.tree_from = tree_versions[0].tree
        self.tree_to_fill = tree_versions[1].tree

        self.cmd = FillProgramTreeContentFromLastYearCommand(
            to_year=self.tree_to_fill.entity_id.year,
            to_code=self.tree_to_fill.entity_id.code
        )

        self.mock_copy_cms()
        self.create_node_next_years(self.tree_from.get_all_learning_unit_nodes())

    def create_node_next_years(self, nodes):
        for node in nodes:
            if node.is_learning_unit():
                next_year_node = node_factory.copy_to_next_year(node)
                self.add_node_to_repo(next_year_node)

    def mock_copy_cms(self):
        patcher = mock.patch(
            "program_management.ddd.domain.service.copy_tree_cms.CopyCms.from_tree",
            side_effect=lambda *args, **kwargs: None
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def mock_copy_group(self):
        patcher = mock.patch(
            "education_group.ddd.service.write.copy_group_service.copy_group",
            side_effect=lambda node: self.add_node_to_repo(node_factory.copy_to_next_year(node))
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_should_work_with_group(self):
        result = fill_program_tree_content_from_last_year_service.fill_program_tree_content_from_last_year(self.cmd)

        self.assertTrue(result)

    def test_should_persist(self):
        fill_program_tree_content_from_last_year_service.fill_program_tree_content_from_last_year(self.cmd)

        expected = [
            attr.evolve(child_node.entity_id, year=child_node.entity_id.year+1)
            for child_node in self.tree_from.root_node.get_all_children_as_nodes()
        ]
        actual = [
            child_node.entity_id
            for child_node in self.tree_to_fill.root_node.get_all_children_as_nodes()
        ]
        self.assertCountEqual(expected, actual)
