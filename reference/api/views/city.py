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
from django.db.models import F
from django_filters import rest_framework as filters
from rest_framework import generics

from reference.api.serializers.city import CitySerializer
from reference.models.zipcode import ZipCode


class CityFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="municipality", lookup_expr='icontains')
    country_iso_code = filters.CharFilter(field_name="country__iso_code", lookup_expr="icontains")
    zip_code = filters.CharFilter(field_name="zip_code", lookup_expr="icontains")


class CityList(generics.ListAPIView):
    """
       Return a list of all the city.
    """
    name = 'city-list'
    queryset = ZipCode.objects.all().annotate(
        country_iso_code=F('country__iso_code'),
        name=F('municipality')
    )
    serializer_class = CitySerializer
    filterset_class = CityFilter
    search_fields = (
        'zip_code',
        'country_iso_code',
        'name',
    )
    ordering_fields = (
        'zip_code',
        'name',
    )
    ordering = (
        'zip_code',
    )  # Default ordering
