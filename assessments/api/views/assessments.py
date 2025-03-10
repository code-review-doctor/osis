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
from django.http import Http404
from rest_framework import generics

from assessments.api.serializers.session import SessionSerializer
from base.models import session_exam_calendar
from base.models.academic_year import AcademicYear


class CurrentSessionExamView(generics.RetrieveAPIView):
    name = 'current_session'
    serializer_class = SessionSerializer

    def get_object(self):
        current_event = session_exam_calendar.current_session_exam()
        return _build_session(current_event)


class NextSessionExamView(generics.RetrieveAPIView):
    name = 'next_session'
    serializer_class = SessionSerializer

    def get_object(self):
        current_event = session_exam_calendar.get_closest_new_session_exam()
        return _build_session(current_event)


class PreviousSessionExamView(generics.RetrieveAPIView):
    name = 'previous_session'
    serializer_class = SessionSerializer

    def get_object(self):
        current_event = session_exam_calendar.get_latest_session_exam()

        if current_event:
            current_academic_year = AcademicYear.objects.get(year=current_event.authorized_target_year)
            return {
                'start_date': current_event.start_date,
                'end_date': current_event.end_date,
                'year': current_academic_year.year,
                'month_session_name': current_event.month_session_name()
            }
        return None


def _build_session(current_event):
    if current_event:
        current_academic_year = AcademicYear.objects.get(year=current_event.authorized_target_year)
        return {
            'start_date': current_event.start_date,
            'end_date': current_event.end_date,
            'year': current_academic_year.year,
            'month_session_name': current_event.month_session_name()
        }
    raise Http404
