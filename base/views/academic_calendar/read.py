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
import itertools

from typing import Dict, List

from django.views.generic import TemplateView

from base.business.event_perms import AcademicEventFactory
from base.models.enums.academic_calendar_type import AcademicCalendarTypes
from osis_role.contrib.views import PermissionRequiredMixin


class AcademicCalendarsView(PermissionRequiredMixin, TemplateView):
    permission_required = 'base.can_access_academic_calendar'
    raise_exception = True

    template_name = "academic_calendar/academic_calendars.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'gantt_rows': self.get_gantt_rows()
        }

    def get_gantt_rows(self) -> List[Dict]:
        academic_events = AcademicEventFactory().get_academic_events()
        academic_events = sorted(academic_events, key=lambda row: row.type)

        gantt_rows = []
        for type, events in itertools.groupby(academic_events, lambda row: row.type):
            gantt_rows.append({
                'id': type,
                'text': AcademicCalendarTypes.get_value(type),
                'divider': 'true',
                'color': '#337ab7'
            })

            events = sorted(events, key=lambda row: row.authorized_target_year)
            gantt_rows += [{
                'text': str(event.authorized_target_year),
                'tooltip_text': "{} - {}".format(
                    AcademicCalendarTypes.get_value(type),
                    str(event.authorized_target_year)
                ),
                'start_date': event.start_date.strftime('%d-%m-%Y'),
                'end_date': event.end_date.strftime('%d-%m-%Y') if event.end_date else '',
                'parent': type
            } for event in events]
        return gantt_rows
