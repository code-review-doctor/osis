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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
import random
from typing import List, Union

import factory

from base.business.academic_calendar import AcademicEventRepository, AcademicEvent, AcademicSessionEvent
from base.models.enums.academic_calendar_type import AcademicCalendarTypes


class AcademicEventInMemoryRepository(AcademicEventRepository):
    def __init__(self):
        self.events = []  # type: List[Union[AcademicEvent, AcademicSessionEvent]]

    def get_academic_events(self, event_reference: str = None) -> List[Union[AcademicEvent, AcademicSessionEvent]]:
        return [event for event in self.events if event.type == event_reference]

    def get(self, academic_event_id: int) -> Union[AcademicEvent, AcademicSessionEvent]:
        return next(event for event in self.events if event.id == academic_event_id)

    def update(self, academic_event: Union[AcademicEvent, AcademicSessionEvent]):
        old_event = next(
            (event for event in self.events if event.id == academic_event.id),
            None
        )
        if old_event:
            self.events.remove(old_event)
        self.events.append(academic_event)


class AcademicEventFactory(factory.Factory):
    class Meta:
        model = AcademicEvent
        abstract = False

    id = factory.Sequence(lambda n: n)
    title = "Academic Event"
    authorized_target_year = 2021
    start_date = factory.LazyFunction(lambda: datetime.date(2021, 9, 15))
    end_date = factory.LazyFunction(lambda: datetime.date(2021, 11, 18))
    type = AcademicCalendarTypes.COURSE_ENROLLMENT.name


class AcademicSessionEventFactory(AcademicEventFactory):
    class Meta:
        model = AcademicSessionEvent
        abstract = False

    session = 1


class AttendanceMarkSession1Factory(AcademicSessionEventFactory):
    title = "Demande de note de présence - Session 1"
    start_date = factory.LazyFunction(lambda: datetime.date(2021, 12, 15))
    end_date = factory.LazyFunction(lambda: datetime.date(2022, 2, 28))
    type = AcademicCalendarTypes.ATTENDANCE_MARK.name


class ScoreEncodingSession1Factory(AcademicSessionEventFactory):
    title = "Encodage de notes - Session 1"
    start_date = factory.LazyFunction(lambda: datetime.date(2021, 12, 15))
    end_date = factory.LazyFunction(lambda: datetime.date(2022, 2, 28))
    type = AcademicCalendarTypes.SCORES_EXAM_SUBMISSION.name
