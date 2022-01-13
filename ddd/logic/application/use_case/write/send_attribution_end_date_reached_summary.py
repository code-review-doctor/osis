##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime

from django.db import transaction

from ddd.logic.application.domain.service.attributions_end_date_reached_summary import \
    IAttributionsEndDateReachedSummary
from ddd.logic.application.repository.i_applicant_respository import IApplicantRepository
from ddd.logic.application.repository.i_application_calendar_repository import IApplicationCalendarRepository
from ddd.logic.effective_class_repartition.builder.academic_year_identity_builder import AcademicYearIdentityBuilder


@transaction.atomic()
def send_emails_to_teachers_with_ending_attributions(
        application_calendar_repository: IApplicationCalendarRepository,
        applicant_repository: IApplicantRepository,
        application_summary: IAttributionsEndDateReachedSummary,
) -> None:

    # GIVEN
    application_calendar = application_calendar_repository.get_current_application_calendar()

    # WHEN
    if application_calendar.start_date == datetime.date.today():
        applicants = applicant_repository.search(year=application_calendar.authorized_target_year.year)
        for applicant in applicants:
            attributions_ending = applicant.get_attributions_about_to_expire(
                AcademicYearIdentityBuilder.build_from_year(application_calendar.authorized_target_year.year)
            )
            if len(attributions_ending) > 0:
                # THEN
                application_summary.send(applicant, attributions_ending, application_calendar.end_date)
