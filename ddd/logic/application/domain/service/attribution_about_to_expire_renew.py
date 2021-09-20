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
from functools import partial
from typing import List

import uuid

from attribution.models.enums.function import Functions
from base.ddd.utils.business_validator import MultipleBusinessExceptions, execute_functions_and_aggregate_exceptions
from ddd.logic.application.domain.model.applicant import Applicant
from ddd.logic.application.domain.model.application import Application, ApplicationIdentity
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar
from ddd.logic.application.domain.model._attribution import Attribution
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity, VacantCourse
from ddd.logic.application.domain.service.apply_on_vacant_course import ApplyOnVacantCourse
from ddd.logic.application.domain.service.i_learning_unit_service import ILearningUnitService
from ddd.logic.application.domain.validator.exceptions import AttributionAboutToExpireNotFound, \
    AttributionAboutToExpireFunctionException, VacantCourseNotFound, AttributionSubstituteException, \
    AttributionAboutToExpireWithoutVolumeException
from ddd.logic.application.dtos import AttributionAboutToExpireDTO
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from osis_common.ddd import interface


class AttributionAboutToExpireRenew(interface.DomainService):

    @classmethod
    def check_renew(
            cls,
            vacant_course: VacantCourse,
            all_existing_applications: List[Application],
            attribution_about_to_expire: Attribution
    ):
        execute_functions_and_aggregate_exceptions(
            partial(_should_attribution_about_to_expire_with_volume, attribution_about_to_expire),
            partial(_should_not_be_a_substitute, attribution_about_to_expire),
            partial(
                ApplyOnVacantCourse.check_apply,
                vacant_course,
                all_existing_applications,
                attribution_about_to_expire.lecturing_volume,
                attribution_about_to_expire.practical_volume
            )
        )

    @classmethod
    def get_list_with_renewal_availability(
            cls,
            application_calendar: ApplicationCalendar,
            applicant: Applicant,
            all_existing_applications: List[Application],
            vacant_course_repository: IVacantCourseRepository,
            learning_unit_service: ILearningUnitService,
    ) -> List[AttributionAboutToExpireDTO]:
        attributions_about_to_expire = applicant.get_attributions_about_to_expire(
            AcademicYearIdentityBuilder.build_from_year(application_calendar.authorized_target_year.year - 1)
        )
        attributions_filtered = _filter_attribution_by_renewable_functions(attributions_about_to_expire)
        if not attributions_about_to_expire:
            return []

        # Lookup vacant course on next year for current attribution
        vacant_course_ids = [
            VacantCourseIdentity(
                academic_year=AcademicYearIdentityBuilder.build_from_year(
                    year=application_calendar.authorized_target_year.year
                ),
                code=attribution.course_id.code
            ) for attribution in attributions_filtered
        ]
        vacant_courses = vacant_course_repository.search(vacant_course_ids)

        learning_unit_ids = [
            LearningUnitIdentity(academic_year=vacant_course_id.academic_year, code=vacant_course_id.code)
            for vacant_course_id in vacant_course_ids
        ]
        vacant_courses_volumes = learning_unit_service.search_learning_unit_volumes_dto(learning_unit_ids)

        attributions_about_to_expire_dto = []
        for attribution_about_to_expire in attributions_filtered:
            unavailable_renewal_reason = _get_unavailable_renewal_reason(
                attribution_about_to_expire,
                vacant_courses,
                all_existing_applications
            )
            vacant_course_next_year = _get_vacant_course_by_code(
                attribution_about_to_expire.course_id.code, vacant_courses
            )
            vacant_course_next_year_volume = next((
                vc_volume for vc_volume in vacant_courses_volumes
                if vc_volume.code == attribution_about_to_expire.course_id.code
            ), None)

            attribution_dto = AttributionAboutToExpireDTO(
                code=attribution_about_to_expire.course_id.code,
                year=attribution_about_to_expire.course_id.year,
                lecturing_volume=attribution_about_to_expire.lecturing_volume,
                practical_volume=attribution_about_to_expire.practical_volume,
                function=attribution_about_to_expire.function,
                end_year=attribution_about_to_expire.end_year.year,
                start_year=attribution_about_to_expire.start_year.year,
                title=getattr(vacant_course_next_year, 'title', None) or attribution_about_to_expire.course_title,
                total_lecturing_volume_course=getattr(vacant_course_next_year_volume, 'lecturing_volume_total', None),
                total_practical_volume_course=getattr(vacant_course_next_year_volume, 'practical_volume_total', None),
                lecturing_volume_available=getattr(vacant_course_next_year, 'lecturing_volume_available', None),
                practical_volume_available=getattr(vacant_course_next_year, 'practical_volume_available', None),
                unavailable_renewal_reason=unavailable_renewal_reason,
                is_renewable=unavailable_renewal_reason is None,
            )
            attributions_about_to_expire_dto.append(attribution_dto)

        return attributions_about_to_expire_dto

    @classmethod
    def renew(
            cls,
            learning_unit_code: str,
            application_calendar: ApplicationCalendar,
            applicant: Applicant,
            all_existing_applications: List[Application],
            vacant_course_repository: IVacantCourseRepository
    ) -> Application:
        attributions_about_to_expire = applicant.get_attributions_about_to_expire(
            AcademicYearIdentityBuilder.build_from_year(application_calendar.authorized_target_year.year - 1)
        )
        attributions_filtered = _filter_attribution_by_code(attributions_about_to_expire, learning_unit_code)
        attributions_filtered = _filter_attribution_by_renewable_functions(attributions_filtered)
        if not attributions_filtered:
            raise MultipleBusinessExceptions(exceptions={AttributionAboutToExpireFunctionException()})
        attribution_about_to_expire = attributions_filtered[0]

        vacant_course = vacant_course_repository.get(
            VacantCourseIdentity(
                academic_year=AcademicYearIdentityBuilder.build_from_year(
                    year=application_calendar.authorized_target_year.year
                ),
                code=learning_unit_code
            )
        )

        cls.check_renew(vacant_course, all_existing_applications, attribution_about_to_expire)
        return Application(
            entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
            applicant_id=applicant.entity_id,
            vacant_course_id=vacant_course.entity_id,
            lecturing_volume=attribution_about_to_expire.lecturing_volume,
            practical_volume=attribution_about_to_expire.practical_volume,
            course_summary='',
            remark=''
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
        if attribution_about_to_expire.function in (Functions.CO_HOLDER, Functions.HOLDER)
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
        return VacantCourseNotFound().message

    try:
        AttributionAboutToExpireRenew.check_renew(
            vacant_course_next_year,
            all_existing_applications,
            attribution_about_to_expire
        )
    except MultipleBusinessExceptions as e:
        first_exception = next(iter(e.exceptions))
        return first_exception.message


def _get_vacant_course_by_code(code: str, vacant_courses: List[VacantCourse]):
    return next((vac_course for vac_course in vacant_courses if vac_course.code == code), None)


def _should_attribution_about_to_expire_with_volume(attribution_about_to_expire: Attribution):
    if not attribution_about_to_expire.practical_volume and not attribution_about_to_expire.lecturing_volume:
        raise AttributionAboutToExpireWithoutVolumeException()


def _should_not_be_a_substitute(attribution_about_to_expire: Attribution):
    if attribution_about_to_expire.is_substitute:
        raise AttributionSubstituteException()
