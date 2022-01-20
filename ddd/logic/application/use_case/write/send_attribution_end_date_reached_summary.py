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
import logging

from django.conf import settings
from django.db import transaction

from ddd.logic.application.domain.service.attributions_end_date_reached_summary import \
    IAttributionsEndDateReachedSummary
from ddd.logic.application.repository.i_applicant_respository import IApplicantRepository
from ddd.logic.application.repository.i_application_calendar_repository import IApplicationCalendarRepository

logger = logging.getLogger(settings.DEFAULT_LOGGER)


@transaction.atomic()
def send_emails_to_teachers_with_ending_attributions(
        application_calendar_repository: IApplicationCalendarRepository,
        applicant_repository: IApplicantRepository,
        application_summary: IAttributionsEndDateReachedSummary,
) -> None:
    logger.info("In function send_emails_to_teachers_with_ending_attributions")
    # GIVEN
    application_calendar = application_calendar_repository.get_current_application_calendar()

    # WHEN
    application_summary.send(application_calendar, applicant_repository)
