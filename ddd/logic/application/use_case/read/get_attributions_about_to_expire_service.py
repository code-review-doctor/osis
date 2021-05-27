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

from ddd.logic.application.commands import GetAttributionsAboutToExpireCommand
from ddd.logic.application.domain.model.applicant import ApplicantIdentity
from ddd.logic.application.domain.service.attributionabouttoexpirerenew import AttributionAboutToExpireRenew
from ddd.logic.application.dtos import AttributionAboutToExpireDTO
from ddd.logic.application.repository.i_applicant_respository import IApplicantRepository
from ddd.logic.application.repository.i_application_calendar_repository import IApplicationCalendarRepository
from ddd.logic.application.repository.i_application_repository import IApplicationRepository
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository


def get_attributions_about_to_expire(
        cmd: GetAttributionsAboutToExpireCommand,
        application_repository: IApplicationRepository,
        application_calendar_repository: IApplicationCalendarRepository,
        applicant_repository: IApplicantRepository,
        vacant_course_repository: IVacantCourseRepository,
) -> List[AttributionAboutToExpireDTO]:
    # Given
    application_calendar = application_calendar_repository.get_current_application_calendar()
    applicant_id = ApplicantIdentity(global_id=cmd.global_id)
    applicant = applicant_repository.get(applicant_id)
    all_existing_applications = application_repository.search(global_id=cmd.global_id)

    return AttributionAboutToExpireRenew.get_list_with_renewal_availability(
        application_calendar,
        applicant,
        all_existing_applications,
        vacant_course_repository
    )
