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
from program_management.ddd.command import GetProgramTreeVersionCommand, PostponeProgramTreeVersionsUntilNPlus6Command
from program_management.ddd.service.read import get_program_tree_version_service
from program_management.ddd.service.write.postpone_program_tree_versions_until_n_plus_6_service import \
    postpone_program_tree_versions_until_n_plus_6

from program_management.tests.ddd.factories.domain.program_tree_version.training.OSIS2M import OSIS2MFactory
from testing.testcases import DDDTestCase


class TestPostponeProgramTreeVersionsUntilNPlus6(DDDTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.cmd = PostponeProgramTreeVersionsUntilNPlus6Command()

    def test_should_stop_postponement_before_if_end_date_inferior_to_postponement_year(self):
        tree_version = OSIS2MFactory(end_year=2025)[0]

        postpone_program_tree_versions_until_n_plus_6(self.cmd)

        self.assertIsNone(
            get_program_tree_version_service.get_program_tree_version(
                GetProgramTreeVersionCommand(
                    acronym=tree_version.entity_id.offer_acronym,
                    version_name=tree_version.version_name,
                    transition_name=tree_version.transition_name,
                    year=2026
                )
            )
        )

    def test_should_postpone_trees_until_n_plus_6(self):
        tree_version = OSIS2MFactory(end_year=2028)[0]

        postpone_program_tree_versions_until_n_plus_6(self.cmd)

        self.assertTrue(
            get_program_tree_version_service.get_program_tree_version(
                GetProgramTreeVersionCommand(
                    acronym=tree_version.entity_id.offer_acronym,
                    version_name=tree_version.version_name,
                    transition_name=tree_version.transition_name,
                    year=2026
                )
            )
        )
