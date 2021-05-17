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
import datetime
from typing import List

from ddd.logic.shared_kernel.academic_year.domain.service.get_current_academic_year import GetCurrentAcademicYear
from education_group.ddd.command import PostponeMiniTrainingsUntilNPlus6Command
from education_group.ddd.domain.mini_training import MiniTrainingIdentity
from education_group.ddd.domain.service import postpone_until_n_plus_6
from education_group.ddd.repository import mini_training as mini_training_repository
from infrastructure.shared_kernel.academic_year.repository import academic_year as academic_year_repository


def postpone_minitrainings_until_n_plus_6(cmd: PostponeMiniTrainingsUntilNPlus6Command) -> List['MiniTrainingIdentity']:
    repo = mini_training_repository.MiniTrainingRepository()
    current_academic_year = GetCurrentAcademicYear().get_starting_academic_year(
        datetime.date.today(),
        academic_year_repository.AcademicYearRepository()

    )
    mini_trainings_to_postpone = repo.search_mini_trainings_last_occurence(current_academic_year.year)

    result = []
    for mini_training in mini_trainings_to_postpone:
        mini_trainings_created = postpone_until_n_plus_6.Postpone().postpone_mini_training(
            current_academic_year,
            mini_training,
            repo
        )

        result += [repo.create(mini_training) for mini_training in mini_trainings_created]

    return result
