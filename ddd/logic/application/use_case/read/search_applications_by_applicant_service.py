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

from ddd.logic.application.commands import SearchApplicationByApplicantCommand
from ddd.logic.application.domain.model.applicant import ApplicantIdentity
from ddd.logic.application.domain.model.application import Application
from ddd.logic.application.repository.i_application_calendar_repository import IApplicationCalendarRepository
from ddd.logic.application.repository.i_application_repository import IApplicationRepository


def search_applications_by_applicant(
        cmd: SearchApplicationByApplicantCommand,
        application_repository: IApplicationRepository,
        application_calendar_repository: IApplicationCalendarRepository,
) -> List[Application]:
    # Given
    application_calendar = application_calendar_repository.get_current_application_calendar()
    applicant_id = ApplicantIdentity(global_id=cmd.global_id)

    # Then
    return application_repository.search(
        applicant_id=applicant_id,
        academic_year_id=application_calendar.authorized_target_year,
    )
