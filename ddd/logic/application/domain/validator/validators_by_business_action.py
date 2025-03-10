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

import attr

from base.ddd.utils.business_validator import TwoStepsMultipleBusinessExceptionListValidator, BusinessValidator
from ddd.logic.application.commands import ApplyOnVacantCourseCommand, UpdateApplicationCommand, \
    DeleteApplicationCommand
from ddd.logic.application.domain.model.application import Application
from ddd.logic.application.domain.model.vacant_course import VacantCourse
from ddd.logic.application.domain.validator._should_be_the_author_of_the_application import \
    ShouldBeTheAuthorOfTheApplication
from ddd.logic.application.domain.validator._should_lecturing_or_pratical_filled import \
    ShouldLecturingOrPracticalFilledValidator
from ddd.logic.application.domain.validator._should_volumes_asked_lower_or_equal_to_available import \
    ShouldVolumesAskedLowerOrEqualToAvailable


@attr.s(frozen=True, slots=True)
class ApplyOnVacantCourseValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    command = attr.ib(type=ApplyOnVacantCourseCommand)

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return [
            ShouldLecturingOrPracticalFilledValidator(self.command)
        ]

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return []


@attr.s(frozen=True, slots=True)
class UpdateApplicationValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    vacant_course = attr.ib(type=VacantCourse)
    application = attr.ib(type=Application)
    command = attr.ib(type=UpdateApplicationCommand)

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return [
            ShouldLecturingOrPracticalFilledValidator(self.command)
        ]

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldBeTheAuthorOfTheApplication(
                application=self.application,
                global_id=self.command.global_id
            ),
            ShouldVolumesAskedLowerOrEqualToAvailable(
                vacant_course=self.vacant_course,
                lecturing_volume_asked=self.command.lecturing_volume,
                practical_volume_asked=self.command.practical_volume
            ),
        ]


@attr.s(frozen=True, slots=True)
class DeleteApplicationValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    application = attr.ib(type=Application)
    command = attr.ib(type=DeleteApplicationCommand)

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
               ShouldBeTheAuthorOfTheApplication(
                   application=self.application,
                   global_id=self.command.global_id
               ),
        ]
