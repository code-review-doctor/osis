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
from datetime import datetime
from typing import List

from attribution.models.enums import function
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.application.domain.builder.application_builder import ApplicationBuilder
from ddd.logic.application.domain.model.applicant import Applicant
from ddd.logic.application.domain.model.application import Application
from ddd.logic.application.domain.model.attribution import Attribution
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity
from ddd.logic.application.domain.validator.exceptions import AttributionAboutToExpireNotFound, \
    AttributionAboutToExpireFunctionException
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from osis_common.ddd import interface


class Renew(interface.DomainService):

    @classmethod
    def renew_from_attribution_about_to_expire(
            cls,
            code: str,
            applicant: Applicant,
            all_existing_applications: List[Application],
            vacant_course_repository: IVacantCourseRepository
    ) -> Application:
        attributions_about_to_expire = applicant.get_attributions_about_to_expire(
            AcademicYearIdentity(year=datetime.now().year)
        )
        attributions_filtered = _filter_attribution_by_code(attributions_about_to_expire, code)
        attributions_filtered = _filter_attribution_by_functions(attributions_filtered)
        attribution_about_to_expire = attributions_filtered[0]

        vacant_course_next_year = vacant_course_repository.get(
            VacantCourseIdentity(
                academic_year=AcademicYearIdentity(year=attribution_about_to_expire.end_year.year + 1),
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


def _filter_attribution_by_functions(attributions_about_to_expire: List[Attribution]):
    attributions_filtered = [
        attribution_about_to_expire for attribution_about_to_expire in attributions_about_to_expire
        if attribution_about_to_expire.function in (function.CO_HOLDER, function.HOLDER)
    ]
    if not attributions_filtered:
        raise MultipleBusinessExceptions(exceptions={AttributionAboutToExpireFunctionException()})
    return attributions_filtered
