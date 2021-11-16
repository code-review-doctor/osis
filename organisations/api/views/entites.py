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
from django.db.models import Q, Max
from django_filters import rest_framework as filters
from rest_framework import generics

from base.models.entity_version import EntityVersion
from base.models.enums.entity_type import EntityType
from organisations.api.serializers.entites import EntitesSerializer


class EntitesFilter(filters.FilterSet):
    entity_type = filters.MultipleChoiceFilter(
        field_name='entity_type',
        choices=EntityType.choices()
    )
    year = filters.NumberFilter(method="filter_by_year")

    @staticmethod
    def filter_by_year(queryset, name, value):
        last_start_dates = queryset.filter(
            Q(end_date__isnull=True) | Q(end_date__year__gte=value),
            start_date__year__lte=value
        ).values('entity_id').annotate(max_start_date=Max('start_date'))
        # It's useful to get the last version if there are multiple version inside on academic year

        q_statement = Q()
        for pair in last_start_dates:
            q_statement |= (Q(entity_id=pair['entity_id']) & Q(start_date=pair['max_start_date']))

        return queryset.filter(q_statement)


class EntitesListView(generics.ListAPIView):
    """
       Return all entities
    """
    name = 'entites_ucl'
    serializer_class = EntitesSerializer
    filterset_class = EntitesFilter
    ordering = ('acronym',)

    def get_queryset(self):
        return EntityVersion.objects.filter(
            entity__organization__acronym__iexact=self.kwargs['organisation_code']
        )
