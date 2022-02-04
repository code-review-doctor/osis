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

from rest_framework import serializers

from reference.models.high_school import HighSchool


class HighSchoolListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='reference_api_v1:high_school-detail', lookup_field='uuid')
    name = serializers.CharField(read_only=True)
    acronym = serializers.CharField(read_only=True)

    class Meta:
        model = HighSchool
        fields = (
            'url',
            'uuid',
            'name',
            'acronym',
            'type',
        )


class HighSchoolDetailSerializer(HighSchoolListSerializer):
    linguistic_regime = serializers.CharField(read_only=True, source='linguistic_regime.code')
    zipcode = serializers.CharField(read_only=True, source='zip_code.zip_code')
    city = serializers.CharField(read_only=True, source='zip_code.municipality')
    country = serializers.CharField(read_only=True, source='zip_code.country.iso_code')

    class Meta(HighSchoolListSerializer.Meta):
        fields = HighSchoolListSerializer.Meta.fields + (
            'phone',
            'fax',
            'email',
            'start_year',
            'end_year',
            'linguistic_regime',
            'country',
            'zipcode',
            'city',
            'street',
            'street_number',
        )
