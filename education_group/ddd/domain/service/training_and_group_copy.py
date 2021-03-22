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
from education_group.ddd import command
from education_group.ddd.domain.exception import CannotCopyTrainingDueToLimitYearOfModification
from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.service.write import copy_training_service, copy_group_service


def copy_training_to_next_year(
        postpone_cmd: command.PostponeTrainingAndGroupModificationCommand,
        year: int
) -> 'TrainingIdentity':
    try:
        identity_next_year = copy_training_service.copy_training_to_next_year(
            copy_cmd=command.CopyTrainingToNextYearCommand(
                acronym=postpone_cmd.postpone_from_acronym,
                postpone_from_year=year
            )
        )

        copy_group_service.copy_group(
            cmd=command.CopyGroupCommand(
                from_code=postpone_cmd.code,
                from_year=year
            )
        )
        return identity_next_year
    except CannotCopyTrainingDueToLimitYearOfModification as e:
        return None
