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

from attribution.models.enums import function
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.application.domain.builder.application_builder import ApplicationBuilder
from ddd.logic.application.domain.model.applicant import Applicant
from ddd.logic.application.domain.model.application import Application
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar
from ddd.logic.application.domain.model.attribution import Attribution
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity, VacantCourse
from ddd.logic.application.domain.validator.exceptions import AttributionAboutToExpireNotFound, \
    AttributionAboutToExpireFunctionException
from ddd.logic.application.domain.validator.validators_by_business_action import RenewApplicationValidatorList
from ddd.logic.application.dtos import AttributionAboutToExpireDTO
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from osis_common.ddd import interface


class Renew(interface.DomainService):

    @classmethod
    def get_attributions_about_to_expires(
            cls,
            application_calendar: ApplicationCalendar,
            applicant: Applicant,
            all_existing_applications: List[Application],
            vacant_course_repository: IVacantCourseRepository
    ) -> List[AttributionAboutToExpireDTO]:
        attributions_about_to_expire = applicant.get_attributions_about_to_expire(
            application_calendar.authorized_target_year
        )
        attributions_filtered = _filter_attribution_by_renewable_functions(attributions_about_to_expire)

        # Lookup vacant course on next year for current attribution
        vacant_course_ids = [
            VacantCourseIdentity(
                academic_year=AcademicYearIdentity(year=application_calendar.authorized_target_year.year + 1),
                code=attribution.course_id.code
            ) for attribution in attributions_filtered
        ]
        vacant_courses_next_year = vacant_course_repository.search(vacant_course_ids)

        attributions_about_to_expire_dto = []
        for attribution_about_to_expire in attributions_filtered:
            unavailable_renewal_reason = _get_unavailable_renewal_reason(
                attribution_about_to_expire,
                vacant_courses_next_year,
                all_existing_applications
            )
            vacant_course_next_year = _get_vacant_course_by_code(
                attribution_about_to_expire.course_id.code, vacant_courses_next_year
            )

            attribution_dto = AttributionAboutToExpireDTO(
                code=attribution_about_to_expire.course_id.code,
                year=attribution_about_to_expire.course_id.year,
                title=vacant_course_next_year.title,
                lecturing_volume=attribution_about_to_expire.lecturing_volume,
                practical_volume=attribution_about_to_expire.practical_volume,
                function=attribution_about_to_expire.function,
                end_year=attribution_about_to_expire.end_year,
                start_year=attribution_about_to_expire.start_year,
                total_lecturing_volume_course=vacant_course_next_year.lecturing_volume_total,
                total_practical_volume_course=vacant_course_next_year.practical_volume_total,
                lecturing_volume_available=vacant_course_next_year.lecturing_volume_available,
                practical_volume_available=vacant_course_next_year.practical_volume_available,
                unavailable_renewal_reason=unavailable_renewal_reason,
                is_renewable=unavailable_renewal_reason is None,
            )
            attributions_about_to_expire_dto.append(attribution_dto)

        return attributions_about_to_expire_dto

    @classmethod
    def renew_from_attribution_about_to_expire(
            cls,
            code: str,
            application_calendar: ApplicationCalendar,
            applicant: Applicant,
            all_existing_applications: List[Application],
            vacant_course_repository: IVacantCourseRepository
    ) -> Application:
        attributions_about_to_expire = applicant.get_attributions_about_to_expire(
            application_calendar.authorized_target_year
        )
        attributions_filtered = _filter_attribution_by_code(attributions_about_to_expire, code)
        attributions_filtered = _filter_attribution_by_renewable_functions(attributions_filtered)
        if not attributions_filtered:
            raise MultipleBusinessExceptions(exceptions={AttributionAboutToExpireFunctionException()})
        attribution_about_to_expire = attributions_filtered[0]

        # Lookup vacant course on next year
        vacant_course_next_year = vacant_course_repository.get(
            VacantCourseIdentity(
                academic_year=AcademicYearIdentity(year=application_calendar.authorized_target_year.year + 1),
                code=code
            )
        )

        return ApplicationBuilder.build_from_attribution_about_to_expire(
            applicant,
            vacant_course_next_year,
            attribution_about_to_expire,
            all_existing_applications
        )


def _filter_attribution_by_code(attributions_about_to_expire: List[Attribution], code: str):
    attributions_filtered = [
        attribution_about_to_expire for attribution_about_to_expire in attributions_about_to_expire
        if attribution_about_to_expire.course_id.code == code
    ]
    if not attributions_filtered:
        raise MultipleBusinessExceptions(exceptions={AttributionAboutToExpireNotFound(code=code)})
    return attributions_filtered


def _filter_attribution_by_renewable_functions(attributions_about_to_expire: List[Attribution]):
    return [
        attribution_about_to_expire for attribution_about_to_expire in attributions_about_to_expire
        if attribution_about_to_expire.function in (function.CO_HOLDER, function.HOLDER)
    ]


def _get_unavailable_renewal_reason(
        attribution_about_to_expire: Attribution,
        vacant_courses_next_year: List[VacantCourse],
        all_existing_applications: List[Application]
) -> str:
    vacant_course_next_year = _get_vacant_course_by_code(
        attribution_about_to_expire.course_id.code, vacant_courses_next_year
    )
    if vacant_course_next_year is None:
        return "No vacant corresponding activity"

    try:
        RenewApplicationValidatorList(
            vacant_course=vacant_course_next_year,
            attribution_about_to_expire=attribution_about_to_expire,
            all_existing_applications=all_existing_applications
        ).validate()
    except MultipleBusinessExceptions as e:
        first_exception = next(iter(e.exceptions))
        return first_exception.message


def _get_vacant_course_by_code(code: str, vacant_courses: List[VacantCourse]):
    return next((vac_course for vac_course in vacant_courses if vac_course.code == code), None)
