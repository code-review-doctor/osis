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
import mock

from education_group.ddd.domain import mini_training
from education_group.ddd.service.write import create_orphan_mini_training_service
from education_group.tests.ddd.factories.command.create_mini_training_command import CreateMiniTrainingCommandFactory
from testing.testcases import DDDTestCase


@mock.patch("education_group.ddd.service.write.create_orphan_mini_training_service."
            "create_group_service.create_orphan_group", return_value=[])
@mock.patch("education_group.ddd.service.write.create_orphan_mini_training_service."
            "postpone_mini_training_and_orphan_group_modifications_service."
            "postpone_mini_training_and_orphan_group_modifications",
            return_value=[])
class TestCreateAndPostponeOrphanMiniTraining(DDDTestCase):
    def test_should_return_mini_training_identities(self, mock_postpone_mini_training, mock_create_orphan_group):
        mock_postpone_mini_training.return_value = [
            mini_training.MiniTrainingIdentity(acronym="ACRON", year=year) for year in range(2020, 2023)
        ]

        cmd = CreateMiniTrainingCommandFactory(year=2020, code="CODE", abbreviated_title="ACRON")
        result = create_orphan_mini_training_service.create_and_postpone_orphan_mini_training(cmd)

        expected_result = [mini_training.MiniTrainingIdentity(acronym="ACRON", year=year) for year in range(2020, 2023)]
        self.assertListEqual(expected_result, result)

    def test_should_call_postpone_mini_training_service(self, mock_postpone_mini_training, mock_create_orphan_group):
        cmd = CreateMiniTrainingCommandFactory(year=2020, code="CODE", abbreviated_title="ACRON")

        create_orphan_mini_training_service.create_and_postpone_orphan_mini_training(cmd)
        self.assertTrue(mock_postpone_mini_training.called)

    def test_should_call_create_orphan_group_service(self, mock_postpone_mini_training, mock_create_orphan_group):
        cmd = CreateMiniTrainingCommandFactory(year=2020, code="CODE", abbreviated_title="ACRON")

        create_orphan_mini_training_service.create_and_postpone_orphan_mini_training(cmd)
        self.assertTrue(mock_create_orphan_group.called)
