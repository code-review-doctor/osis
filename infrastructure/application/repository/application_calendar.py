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
from attribution.calendar.application_courses_calendar import ApplicationCoursesCalendar
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar, ApplicationCalendarIdentity
from ddd.logic.application.repository.i_application_calendar_repository import IApplicationCalendarRepository


class ApplicationCalendarRepository(IApplicationCalendarRepository):
    @classmethod
    def get_current_application_calendar(cls) -> ApplicationCalendar:
        academic_events = ApplicationCoursesCalendar().get_opened_academic_events()
        academic_event = academic_events[0] if academic_events else None
        if academic_event:
            return ApplicationCalendar(
                entity_id=ApplicationCalendarIdentity(uuid=academic_event.id),
                authorized_target_year=academic_event.authorized_target_year,
                start_date='',
                end_date='',
            )
        return None
