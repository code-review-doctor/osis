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

from program_management.ddd import command
from program_management.ddd.domain.exception import CannotPasteToLearningUnitException
from program_management.ddd.domain.program_tree import build_path
from program_management.ddd.service.read import check_paste_node_service
from program_management.tests.ddd.factories.domain.program_tree_version.mini_training.MINECON import MINECONFactory
from program_management.tests.ddd.factories.domain.program_tree_version.training.OSIS1BA import OSIS1BAFactory
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory
from testing.testcases import DDDTestCase


class TestCheckPasteNodeService(DDDTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.tree_version = OSIS1BAFactory()[0]
        self.tree = self.tree_version.tree

        self.learning_unit_node = NodeLearningUnitYearFactory(year=self.tree.root_node.year, persist=True)
        self.mini_training_version = MINECONFactory()[0]

        path = build_path(
            self.tree.root_node,
            self.tree.get_node_by_code_and_year("LOSIS101T", self.tree.root_node.year),
            self.tree.get_node_by_code_and_year("LOSIS102R", self.tree.root_node.year),
        )

        self.cmd = command.CheckPasteNodeCommand(
            node_to_paste_code=self.learning_unit_node.code,
            node_to_paste_year=self.learning_unit_node.year,
            path_to_paste=path,
            path_to_detach=None,
            root_id=self.tree.root_node.node_id
        )

    def test_cannot_paste_node_to_learning_unit_node(self):
        path = build_path(
            self.tree.root_node,
            self.tree.get_node_by_code_and_year("LOSIS101T", self.tree.root_node.year),
            self.tree.get_node_by_code_and_year("LOSIS102R", self.tree.root_node.year),
            self.tree.get_node_by_code_and_year("LDROI1001", self.tree.root_node.year),
        )
        cmd = attr.evolve(self.cmd, path_to_paste=path)

        with self.assertRaisesBusinessException(CannotPasteToLearningUnitException):
            check_paste_node_service.check_paste(cmd)

    def test_should_return_none_when_checks_pass(self):
        self.assertIsNone(
            check_paste_node_service.check_paste(self.cmd)
        )
