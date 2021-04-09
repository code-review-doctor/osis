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

from program_management.ddd import command
from program_management.ddd.domain.exception import ProgramTreeNotFoundException, ProgramTreeNonEmpty, \
    NodeHaveLinkException
from program_management.ddd.service.read import get_program_tree_service
from program_management.ddd.service.write import delete_all_program_tree_service
from program_management.tests.ddd.factories.domain.program_tree.trainings.OSIS1BA import BisProgramTreeBachelorFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from testing.testcases import DDDTestCase


class TestDeleteAllProgramTreeService(DDDTestCase):
    def setUp(self):
        super().setUp()
        self.trees = ProgramTreeFactory.multiple(4, root_node__year=2018, root_node__code='LOSIS100B', persist=True)
        self.cmd = command.DeleteAllProgramTreeCommand(code='LOSIS100B')

    def test_cannot_delete_tree_that_are_not_empty(self):
        non_empty_trees = BisProgramTreeBachelorFactory.multiple(3, current_year=2018, end_year=2025, persist=True)

        cmd = attr.evolve(self.cmd, code=non_empty_trees[0].root_node.code)

        with self.assertRaises(ProgramTreeNonEmpty):
            delete_all_program_tree_service.delete_all_program_tree(cmd)

    def test_cannot_delete_trees_that_are_used(self):
        bachelors = BisProgramTreeBachelorFactory.multiple(3, current_year=2018, end_year=2025, persist=True)

        cmd = attr.evolve(self.cmd, code='LINFO102R')

        with self.assertRaises(NodeHaveLinkException):
            delete_all_program_tree_service.delete_all_program_tree(cmd)

    def test_should_return_program_tree_identities(self):
        result = delete_all_program_tree_service.delete_all_program_tree(self.cmd)

        expected = [tree.entity_id for tree in self.trees]
        self.assertListEqual(expected, result)

    def test_should_suppress_all_program_trees_with_same_code(self):
        identities_of_tree_deleted = delete_all_program_tree_service.delete_all_program_tree(self.cmd)

        for tree_identity in identities_of_tree_deleted:
            with self.subTest(identity=tree_identity):
                with self.assertRaises(ProgramTreeNotFoundException):
                    get_program_tree_service.get_program_tree(
                        command.GetProgramTree(code=tree_identity.code, year=tree_identity.year)
                    )
