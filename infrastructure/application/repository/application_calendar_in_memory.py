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
import datetime
from typing import List

from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar
from ddd.logic.application.repository.i_application_calendar_repository import IApplicationCalendarRepository


class ApplicationCalendarInMemoryRepository(IApplicationCalendarRepository):
    application_calendars = []

    # TODO remove this and change classmethod to instance method save/search/...
    def __init__(self, application_calendars: List[ApplicationCalendar] = None):
        ApplicationCalendarInMemoryRepository.application_calendars = application_calendars or []

    @classmethod
    def get_current_application_calendar(cls) -> ApplicationCalendar:
        today = datetime.date.today()

        return next(
            application_calendar for application_calendar in cls.application_calendars if
            application_calendar.start_date < today <= application_calendar.end_date
        )
