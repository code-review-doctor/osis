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
from django.db.models import F, Case, When, Q, Value, CharField
from django.db.models.functions import Concat
from rest_framework import generics
from rest_framework.response import Response

from attribution.api.serializers.attribution import AttributionSerializer
from attribution.calendar.access_schedule_calendar import AccessScheduleCalendar
from attribution.models.attribution_charge_new import AttributionChargeNew


class AttributionListView(generics.ListAPIView):
    """
       Return all attributions of connected user in a specific year
    """
    name = 'attributions'

    def list(self, request, *args, **kwargs):
        qs = AttributionChargeNew.objects.select_related(
            'attribution',
            'learning_component_year__learning_unit_year__academic_year'
        ).distinct(
            'learning_component_year__learning_unit_year_id'
        ).filter(
            learning_component_year__learning_unit_year__academic_year__year=self.kwargs['year'],
            attribution__tutor__person__user=self.request.user,
            attribution__decision_making=''
        ).annotate(
            code=F('learning_component_year__learning_unit_year__acronym'),
            title_fr=Case(
                When(
                    Q(learning_component_year__learning_unit_year__learning_container_year__common_title__isnull=True) |
                    Q(learning_component_year__learning_unit_year__learning_container_year__common_title__exact=''),
                    then='learning_component_year__learning_unit_year__specific_title'
                ),
                When(
                    Q(learning_component_year__learning_unit_year__specific_title__isnull=True) |
                    Q(learning_component_year__learning_unit_year__specific_title__exact=''),
                    then='learning_component_year__learning_unit_year__learning_container_year__common_title'
                ),
                default=Concat(
                    'learning_component_year__learning_unit_year__learning_container_year__common_title',
                    Value(' - '),
                    'learning_component_year__learning_unit_year__specific_title'
                ),
                output_field=CharField(),
            ),
            title_en=Case(
                When(
                    Q(learning_component_year__learning_unit_year__learning_container_year__common_title_english__isnull=True) |  # noqa
                    Q(learning_component_year__learning_unit_year__learning_container_year__common_title_english__exact=''),  # noqa
                    then='learning_component_year__learning_unit_year__specific_title_english'
                ),
                When(
                    Q(learning_component_year__learning_unit_year__specific_title_english__isnull=True) |
                    Q(learning_component_year__learning_unit_year__specific_title_english__exact=''),
                    then='learning_component_year__learning_unit_year__learning_container_year__common_title_english'
                ),
                default=Concat(
                    'learning_component_year__learning_unit_year__learning_container_year__common_title_english',
                    Value(' - '),
                    'learning_component_year__learning_unit_year__specific_title_english'
                ),
                output_field=CharField(),
            ),
            year=F('learning_component_year__learning_unit_year__academic_year__year'),
            credits=F('learning_component_year__learning_unit_year__credits'),
            start_year=F('attribution__start_year'),
            function=F('attribution__function')
        )
        serializer = AttributionSerializer(qs, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    def get_serializer_context(self):
        return {
            **super().get_serializer_context(),
            'access_schedule_calendar': AccessScheduleCalendar()
        }
