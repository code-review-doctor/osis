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

from program_management.ddd import command
from program_management.ddd.domain.exception import VersionNameExistsCurrentYearAndInFuture
from program_management.ddd.domain.program_tree_version import NOT_A_TRANSITION, \
    ProgramTreeVersionIdentity
from program_management.ddd.service.write import create_and_postpone_tree_specific_version_service
from program_management.tests.ddd.factories.domain.program_tree_version.training.OSIS1BA import OSIS1BAFactory
from testing.testcases import DDDTestCase


class CreateAndPostponeProgramTreeSpecificVersionTestCase(DDDTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.standard_bachelor = OSIS1BAFactory()[0]
        self.cmd = command.CreateProgramTreeSpecificVersionCommand(
            end_year=self.standard_bachelor.end_year.year,
            offer_acronym=self.standard_bachelor.entity_id.offer_acronym,
            version_name="VERSION",
            start_year=self.standard_bachelor.entity_id.year,
            transition_name=NOT_A_TRANSITION,
            title_fr="title in fr",
            title_en="Title in english",
        )

    def test_cannot_create_specific_version_if_version_already_exists_in_the_future(self):
        OSIS1BAFactory.create_specific_version_from_tree_version(
            self.standard_bachelor,
            from_start_year=self.cmd.start_year+2,
            version_name="VERSION"
        )

        with self.assertRaisesBusinessException(VersionNameExistsCurrentYearAndInFuture):
            create_and_postpone_tree_specific_version_service.create_and_postpone_program_tree_specific_version(
                self.cmd
            )

    def test_should_return_tree_version_identities(self):
        result = create_and_postpone_tree_specific_version_service.create_and_postpone_program_tree_specific_version(
            self.cmd
        )

        expected = [
            ProgramTreeVersionIdentity(
                offer_acronym=self.cmd.offer_acronym,
                year=year,
                version_name=self.cmd.version_name,
                transition_name=self.cmd.transition_name
            ) for year in range(self.cmd.start_year, 2026)
        ]
        self.assertEqual(expected, result)
