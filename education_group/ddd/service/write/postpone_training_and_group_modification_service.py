##############################################################################
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List

from education_group.ddd import command
from education_group.ddd.domain import exception
from education_group.ddd.domain.service.conflicted_fields import ConflictedFields
from education_group.ddd.domain.service.training_and_group_copy import PostponeTrainingToNextYear
from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.service.write import update_training_and_group_service
from education_group.ddd.service.write.copy_group_service import copy_group
from education_group.ddd.service.write.copy_training_service import copy_training_to_next_year
from education_group.ddd.service.write.update_training_and_group_service import update_training_and_group
from program_management.ddd.domain.service.calculate_end_postponement import CalculateEndPostponement


def postpone_training_and_group_modification(postpone_cmd: command.PostponeTrainingAndGroupModificationCommand) \
        -> List['TrainingIdentity']:
    # GIVEN
    from_training_id = TrainingIdentity(
        acronym=postpone_cmd.postpone_from_acronym,
        year=postpone_cmd.postpone_from_year
    )
    conflicted_fields = ConflictedFields().get_training_conflicted_fields(from_training_id)

    # WHEN
    identities_created, conflicted_fields = PostponeTrainingToNextYear.postpone(
        postpone_cmd,
        from_training_id,
        conflicted_fields,
        copy_training_to_next_year,
        copy_group,
        update_training_and_group,
        CalculateEndPostponement()
    )
    # THEN
    if conflicted_fields:
        first_conflict_year = min(conflicted_fields.keys())
        raise exception.TrainingCopyConsistencyException(first_conflict_year, conflicted_fields[first_conflict_year])
    return identities_created
