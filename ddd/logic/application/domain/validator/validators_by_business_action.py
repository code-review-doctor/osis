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
from ddd.logic.application.domain.model.attribution import Attribution
from ddd.logic.application.domain.model.vacant_course import VacantCourse
from ddd.logic.application.domain.validator._should_be_the_author_of_the_application import \
    ShouldBeTheAuthorOfTheApplication
from ddd.logic.application.domain.validator._should_attribution_about_to_expire_with_volume import \
    ShouldAttributionAboutToExpireWithVolumeValidator
from ddd.logic.application.domain.validator._should_lecturing_or_pratical_filled import \
    ShouldLecturingOrPracticalFilledValidator
from ddd.logic.application.domain.validator._should_not_be_a_substitute import ShouldNotBeASubstituteValidator
from ddd.logic.application.domain.validator._should_not_have_already_applied_on_vacant_course import \
    ShouldNotHaveAlreadyAppliedOnVacantCourse
from ddd.logic.application.domain.validator._should_vacant_course_allowable_declaration_type import \
    ShouldVacantCourseAllowableDeclarationType
from ddd.logic.application.domain.validator._should_vacant_course_application_not_managed_in_team import \
    ShouldVacantCourseApplicationNotManagedInTeam
from ddd.logic.application.domain.validator._should_volumes_asked_lower_or_equal_to_available import \
    ShouldVolumesAskedLowerOrEqualToAvailable


@attr.s(frozen=True, slots=True)
class ApplyOnVacantCourseValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    command = attr.ib(type=ApplyOnVacantCourseCommand)
    all_existing_applications = attr.ib(type=List[Application])
    vacant_course = attr.ib(type=VacantCourse)

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return [
            ShouldLecturingOrPracticalFilledValidator(self.command)
        ]

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldVacantCourseAllowableDeclarationType(vacant_course=self.vacant_course),
            ShouldNotHaveAlreadyAppliedOnVacantCourse(
                vacant_course=self.vacant_course, all_existing_applications=self.all_existing_applications
            ),
            ShouldVolumesAskedLowerOrEqualToAvailable(
                vacant_course=self.vacant_course,
                lecturing_volume_asked=self.command.lecturing_volume,
                practical_volume_asked=self.command.practical_volume
            ),
            ShouldVacantCourseApplicationNotManagedInTeam(
                vacant_course=self.vacant_course
            )
        ]


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


@attr.s(frozen=True, slots=True)
class RenewApplicationValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    vacant_course = attr.ib(type=VacantCourse)
    attribution_about_to_expire = attr.ib(type=Attribution)
    all_existing_applications = attr.ib(type=List[Application])

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldAttributionAboutToExpireWithVolumeValidator(
                attribution_about_to_expire=self.attribution_about_to_expire
            ),
            ShouldVacantCourseAllowableDeclarationType(vacant_course=self.vacant_course),
            ShouldNotHaveAlreadyAppliedOnVacantCourse(
                vacant_course=self.vacant_course, all_existing_applications=self.all_existing_applications
            ),
            ShouldVolumesAskedLowerOrEqualToAvailable(
                vacant_course=self.vacant_course,
                lecturing_volume_asked=self.attribution_about_to_expire.lecturing_volume,
                practical_volume_asked=self.attribution_about_to_expire.practical_volume
            ),
            ShouldVacantCourseApplicationNotManagedInTeam(
                vacant_course=self.vacant_course
            ),
            ShouldNotBeASubstituteValidator(attribution_about_to_expire=self.attribution_about_to_expire)
        ]
