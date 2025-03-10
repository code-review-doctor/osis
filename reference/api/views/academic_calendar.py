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
from django_filters import rest_framework as filters
from rest_framework import generics

from base.models.academic_calendar import AcademicCalendar
from reference.api.serializers.academic_calendar import AcademicCalendarSerializer


class AcademicCalendarFilter(filters.FilterSet):
    data_year = filters.NumberFilter(field_name='data_year__year')
    reference = filters.CharFilter()


class AcademicCalendarList(generics.ListAPIView):
    """
       Return a list of all the academic calendars.
    """
    name = 'academic-calendar-list'

    queryset = AcademicCalendar.objects.all()
    filterset_class = AcademicCalendarFilter
    serializer_class = AcademicCalendarSerializer
    ordering_fields = (
        'data_year',
        'reference',
    )
    ordering = (
        'data_year',
    )  # Default ordering
