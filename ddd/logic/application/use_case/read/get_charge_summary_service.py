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

from ddd.logic.application.commands import GetChargeSummaryCommand
from ddd.logic.application.domain.builder.applicant_identity_builder import ApplicantIdentityBuilder
from ddd.logic.application.domain.service.charge_summary import ChargeSummary
from ddd.logic.application.domain.service.i_learning_unit_service import ILearningUnitService
from ddd.logic.application.dtos import ChargeSummaryDTO
from ddd.logic.application.repository.i_applicant_respository import IApplicantRepository
from ddd.logic.application.repository.i_application_calendar_repository import IApplicationCalendarRepository
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository


def get_charge_summary(
        cmd: GetChargeSummaryCommand,
        application_calendar_repository: IApplicationCalendarRepository,
        applicant_repository: IApplicantRepository,
        vacant_course_repository: IVacantCourseRepository,
        learning_unit_service: ILearningUnitService
) -> List[ChargeSummaryDTO]:
    # Given
    application_calendar = application_calendar_repository.get_current_application_calendar()
    applicant_id = ApplicantIdentityBuilder.build_from_global_id(global_id=cmd.global_id)
    applicant = applicant_repository.get(applicant_id)

    return ChargeSummary.get(application_calendar, applicant, vacant_course_repository, learning_unit_service)
