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
from education_group.ddd.command import PostponeTrainingsUntilNPlus6Command, GetTrainingCommand
from education_group.ddd.domain.exception import TrainingNotFoundException
from education_group.ddd.service.read import get_training_service
from education_group.ddd.service.write.postpone_trainings_until_n_plus_6_service import \
    postpone_trainings_until_n_plus_6
from education_group.tests.ddd.factories.repository.fake import get_fake_training_repository
from education_group.tests.ddd.factories.training import TrainingFactory
from testing.testcases import DDDTestCase


class TestPostponeTrainingsUntilNPlus6(DDDTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.trainings = [
            TrainingFactory(entity_identity__year=2021, end_year=None, persist=True),
            TrainingFactory(entity_identity__year=2021, end_year=2029, persist=True),
            TrainingFactory(entity_identity__year=2025, end_year=None, persist=True),
        ]

        self.cmd = PostponeTrainingsUntilNPlus6Command()

    def test_should_stop_postponement_before_if_end_date_inferior_to_postponement_year(self):
        training = TrainingFactory(entity_identity__year=2021, end_year=2024)

        postpone_trainings_until_n_plus_6(self.cmd)

        with self.assertRaises(TrainingNotFoundException):
            get_training_service.get_training(GetTrainingCommand(acronym=training.entity_id.acronym, year=2025))

    def test_should_postpone_trainings_until_n_plus_6(self):
        postpone_trainings_until_n_plus_6(self.cmd)

        for training in self.trainings:
            self.assertTrue(
                get_training_service.get_training(GetTrainingCommand(acronym=training.entity_id.acronym, year=2026))
            )
