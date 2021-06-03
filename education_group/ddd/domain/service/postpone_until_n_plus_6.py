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
from typing import List, Optional

from ddd.logic.formation_catalogue.builder.training_builder import TrainingBuilder
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYear
from education_group.ddd.domain.group import GroupBuilder
from education_group.ddd.domain.mini_training import MiniTrainingBuilder
from osis_common.ddd import interface
from education_group.ddd.business_types import *

DEFAULT_YEARS_TO_POSTPONE = 6


class Postpone(interface.DomainService):
    @classmethod
    def postpone_training(
            cls,
            current_academic_year: 'AcademicYear',
            from_training: 'Training',
            training_repository: 'TrainingRepository'
    ) -> List['Training']:
        year_to_postpone_until_to = cls._compute_postponement_until_year(current_academic_year, from_training.end_year)

        result = []
        training_to_copy = from_training
        for year in range(from_training.year, year_to_postpone_until_to):
            training_to_copy = TrainingBuilder().copy_to_next_year(
                training_from=training_to_copy,
                training_repository=training_repository
            )
            result.append(training_to_copy)
        return result

    @classmethod
    def postpone_mini_training(
            cls,
            current_academic_year: 'AcademicYear',
            from_mini_training: 'MiniTraining',
            mini_training_repository: 'MiniTrainingRepository'
    ) -> List['MiniTraining']:
        year_to_postpone_until_to = cls._compute_postponement_until_year(
            current_academic_year,
            from_mini_training.end_year
        )

        result = []
        mini_training_to_copy = from_mini_training
        for year in range(from_mini_training.year, year_to_postpone_until_to):
            mini_training_to_copy = MiniTrainingBuilder().copy_to_next_year(
                mini_training_from=mini_training_to_copy,
                mini_training_repository=mini_training_repository
            )
            result.append(mini_training_to_copy)
        return result

    @classmethod
    def postpone_group(
            cls,
            current_academic_year: 'AcademicYear',
            from_group: 'Group',
            group_repository: 'GroupRepository'
    ) -> List['Group']:
        year_to_postpone_until_to = cls._compute_postponement_until_year(
            current_academic_year,
            from_group.end_year
        )

        result = []
        group_to_copy = from_group
        for year in range(from_group.year, year_to_postpone_until_to):
            group_to_copy = GroupBuilder().copy_to_next_year(
                group_from=group_to_copy,
                group_repository=group_repository
            )
            result.append(group_to_copy)
        return result

    @classmethod
    def _compute_postponement_until_year(cls, current_academic_year: 'AcademicYear', end_year: Optional[int]) -> int:
        max_postponement_year = current_academic_year.year + DEFAULT_YEARS_TO_POSTPONE
        return min(max_postponement_year, end_year) if end_year else max_postponement_year
