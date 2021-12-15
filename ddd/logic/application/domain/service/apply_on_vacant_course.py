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
from decimal import Decimal
from functools import partial
from typing import List, Optional

from base.ddd.utils.business_validator import execute_functions_and_aggregate_exceptions
from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.commands import ApplyOnVacantCourseCommand
from ddd.logic.application.domain.builder.application_builder import ApplicationBuilder
from ddd.logic.application.domain.model.applicant import Applicant
from ddd.logic.application.domain.model.application import Application
from ddd.logic.application.domain.model.vacant_course import VacantCourse
from ddd.logic.application.domain.validator.exceptions import VacantCourseNotAllowedDeclarationType, \
    ApplicationAlreadyExistsException, VolumesAskedShouldBeLowerOrEqualToVolumeAvailable, \
    VacantCourseApplicationManagedInTeamException
from ddd.logic.application.domain.validator.validators_by_business_action import ApplyOnVacantCourseValidatorList
from osis_common.ddd import interface


class ApplyOnVacantCourse(interface.DomainService):

    @classmethod
    def check_apply(
            cls,
            vacant_course: VacantCourse,
            all_existing_applications: List[Application],
            lecturing_volume: Decimal,
            practical_volume: Decimal
    ):
        execute_functions_and_aggregate_exceptions(
            partial(_should_vacant_course_allowable_declaration_type, vacant_course),
            partial(_should_not_have_already_applied_on_vacant_course, vacant_course, all_existing_applications),
            partial(
                _should_volumes_asked_lower_or_equal_to_available,
                vacant_course,
                lecturing_volume,
                practical_volume
            ),
            partial(_should_vacant_course_application_not_managed_in_team, vacant_course)
        )

    @classmethod
    def apply(
            cls,
            applicant: Applicant,
            vacant_course: VacantCourse,
            all_existing_applications: List[Application],
            cmd: ApplyOnVacantCourseCommand
    ) -> Application:
        validator = ApplyOnVacantCourseValidatorList(command=cmd)
        execute_functions_and_aggregate_exceptions(
            validator.validate,
            partial(
                cls.check_apply, vacant_course, all_existing_applications, cmd.lecturing_volume, cmd.practical_volume
            )
        )
        return ApplicationBuilder.build_from_command(applicant, vacant_course, cmd, all_existing_applications)


def _should_vacant_course_allowable_declaration_type(vacant_course: VacantCourse):
    """
       Le cours est bien vacant (Au niveau métier) mais géré dans une procédure séparée
    """
    if vacant_course.vacant_declaration_type not in {VacantDeclarationType.RESEVED_FOR_INTERNS,
                                                     VacantDeclarationType.OPEN_FOR_EXTERNS}:
        raise VacantCourseNotAllowedDeclarationType()


def _should_not_have_already_applied_on_vacant_course(
        vacant_course: VacantCourse,
        all_existing_applications: List[Application]
):
    if vacant_course.entity_id in {application.vacant_course_id for application in all_existing_applications}:
        raise ApplicationAlreadyExistsException()


def _should_volumes_asked_lower_or_equal_to_available(
        vacant_course: VacantCourse,
        lecturing_volume_asked: Optional[Decimal],
        practical_volume_asked: Optional[Decimal],
):
    if (lecturing_volume_asked and lecturing_volume_asked > vacant_course.lecturing_volume_available) or \
            (practical_volume_asked and practical_volume_asked > vacant_course.practical_volume_available):
        raise VolumesAskedShouldBeLowerOrEqualToVolumeAvailable()


def _should_vacant_course_application_not_managed_in_team(vacant_course: VacantCourse):
    if vacant_course.is_in_team:
        raise VacantCourseApplicationManagedInTeamException()
