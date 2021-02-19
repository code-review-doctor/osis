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
from django.test import TestCase

from program_management.ddd.command import GetStandardProgramTreeVersionFromTransitionVersionCommand
from program_management.ddd.service.read.get_standard_program_tree_version_from_transition_version_service import \
    get_standard_program_tree_version_from_transition_version
from program_management.tests.ddd.factories.program_tree_version import ProgramTreeVersionFactory, \
    StandardProgramTreeVersionFactory
from program_management.tests.ddd.factories.repository.fake import get_fake_program_tree_version_repository
from testing.mocks import MockPatcherMixin


class TestGetStandardProgramTreeVersionFromTransitionVersion(TestCase, MockPatcherMixin):
    @classmethod
    def setUpTestData(cls):
        cls.standard_tree = StandardProgramTreeVersionFactory(
            tree__root_node__title="TRANS1458",
            tree__root_node__year=2018,
        )
        cls.transition_tree = StandardProgramTreeVersionFactory(
            tree__root_node__title="TRANS1458",
            tree__root_node__year=2018,
            transition=True
        )

        cls.cmd = GetStandardProgramTreeVersionFromTransitionVersionCommand(
            offer_acronym="TRANS1458",
            year=2018
        )

    def setUp(self) -> None:
        fake_repository = get_fake_program_tree_version_repository([self.standard_tree, self.transition_tree])
        self.mock_repo(
            "program_management.ddd.repositories.program_tree_version.ProgramTreeVersionRepository",
            fake_repository
        )

    def test_should_return_none_when_no_matching_standard_program_tree(self):
        cmd = GetStandardProgramTreeVersionFromTransitionVersionCommand(
            offer_acronym="NOT_EXIST",
            year=2018
        )
        result = get_standard_program_tree_version_from_transition_version(cmd)

        self.assertIsNone(result)

    def test_should_return_standard_tree_when_exists(self):
        result = get_standard_program_tree_version_from_transition_version(self.cmd)

        self.assertEqual(self.standard_tree, result)