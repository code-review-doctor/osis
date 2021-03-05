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
import django_filters as filters
from rest_framework import generics

from reference.api.serializers.study_domain import StudyDomainSerializer
from reference.models.domain import Domain
from reference.models.enums.decree_type import DecreeType


class StudyDomainFilter(filters.FilterSet):
    decree = filters.ChoiceFilter(choices=DecreeType.choices(), field_name='decree__name', method='filter_by_decree')

    class Meta:
        model = Domain
        fields = ['code', 'name']

    @staticmethod
    def filter_by_decree(queryset, name, value):
        return queryset.filter(**{name: DecreeType.get_value(value)})


class StudyDomainList(generics.ListAPIView):
    """
       Return a list of study domains. By default, it will return all official main study domains of 'Paysage'.
    """
    name = 'study_domains_list'
    queryset = Domain.objects.filter(
        parent__isnull=True,
        adhoc=False,
    )
    serializer_class = StudyDomainSerializer
    filterset_class = StudyDomainFilter
    search_fields = (
        'name',
    )
    ordering_fields = (
        'code',
        'name',
    )
    ordering = (
        'name',
    )  # Default ordering
