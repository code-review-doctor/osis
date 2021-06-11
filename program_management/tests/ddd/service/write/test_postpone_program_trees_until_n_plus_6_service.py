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
from program_management.ddd.command import PostponeProgramTreesUntilNPlus6Command, GetProgramTree
from program_management.ddd.domain.exception import ProgramTreeNotFoundException
from program_management.ddd.service.read import get_program_tree_service
from program_management.ddd.service.write.postpone_program_trees_until_n_plus_6_service import \
    postpone_program_trees_until_n_plus_6
from program_management.tests.ddd.factories.domain.program_tree_version.training.OSIS1BA import OSIS1BAFactory
from program_management.tests.ddd.factories.domain.program_tree_version.training.OSIS2M import OSIS2MFactory
from testing.testcases import DDDTestCase


class TestPostponeProgramTreesUntilNPlus6(DDDTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.cmd = PostponeProgramTreesUntilNPlus6Command()

        self.mock_service("program_management.ddd.domain.service.copy_tree_cms.CopyCms.from_tree", return_value=None)

    def test_should_stop_postponement_before_if_end_date_inferior_to_postponement_year(self):
        tree = OSIS2MFactory(end_year=2025)[0].tree

        postpone_program_trees_until_n_plus_6(self.cmd)

        with self.assertRaises(ProgramTreeNotFoundException):
            get_program_tree_service.get_program_tree(GetProgramTree(code=tree.entity_id.code, year=2026))

    def test_should_postpone_trees_until_n_plus_6(self):
        tree = OSIS1BAFactory(end_year=2028, with_postpone=False)[0].tree

        postpone_program_trees_until_n_plus_6(self.cmd)

        self.assertTrue(
            get_program_tree_service.get_program_tree(GetProgramTree(code=tree.entity_id.code, year=2026))
        )
