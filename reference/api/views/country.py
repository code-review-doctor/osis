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

from reference.api.serializers.country import CountrySerializer
from reference.models.country import Country


class CountryFilter(filters.FilterSet):
    not_iso_code = filters.CharFilter(field_name='iso_code', method='exclude_by_iso_code')

    class Meta:
        model = Country
        fields = ['iso_code', 'name', 'name_en', 'dialing_code']

    @staticmethod
    def exclude_by_iso_code(queryset, name, value):
        return queryset.exclude(
            iso_code__in=[iso_code for iso_code in value.split(',')]
        )


class CountryList(generics.ListAPIView):
    """
       Return a list of all the country.
    """
    name = 'country-list'
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_class = CountryFilter
    search_fields = (
        'name',
    )
    ordering_fields = (
        'iso_code',
        'name',
    )
    ordering = (
        'name',
    )  # Default ordering


class CountryDetail(generics.RetrieveAPIView):
    """
        Return the detail of the country
    """
    name = 'country-detail'
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = 'uuid'
