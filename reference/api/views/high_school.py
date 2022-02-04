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
from django.db.models import F
from django_filters import rest_framework as filters
from rest_framework import generics

from reference.api.serializers.high_school import HighSchoolDetailSerializer, \
    HighSchoolListSerializer
from reference.models.high_school import HighSchool


class HighSchoolFilter(filters.FilterSet):
    acronym = filters.CharFilter(field_name="organization__acronym")
    name = filters.CharFilter(field_name="organization__name")
    country = filters.CharFilter(field_name="zip_code__country__iso_code")
    zipcode = filters.CharFilter(field_name="zip_code__zip_code")

    class Meta:
        model = HighSchool
        fields = ['acronym', 'name', 'type', 'country', 'zipcode']


class HighSchoolList(generics.ListAPIView):
    """
       Return a list of all the high school.
    """
    name = 'high_school-list'
    queryset = HighSchool.objects.all().annotate(
        acronym=F('organization__acronym'),
        name=F('organization__name'),
    )
    serializer_class = HighSchoolListSerializer
    filterset_class = HighSchoolFilter
    search_fields = (
        'acronym',
        'name',
    )
    ordering_fields = (
        'acronym',
        'name',
    )


class HighSchoolDetail(generics.RetrieveAPIView):
    """
        Return the detail of the high school.
    """
    name = 'high_school-detail'
    queryset = HighSchool.objects.all().annotate(
        acronym=F('organization__acronym'),
        name=F('organization__name'),
    )
    serializer_class = HighSchoolDetailSerializer
    lookup_field = 'uuid'
