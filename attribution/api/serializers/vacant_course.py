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
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class VacantCourseFilterSerializer(serializers.Serializer):
    allocation_faculty = serializers.CharField(required=False, default=None)
    code = serializers.CharField(required=False, default=None)

    def validate(self, data):
        if not any([data.get('allocation_faculty'), data.get('code')]):
            raise serializers.ValidationError(_("Please precise at least a faculty or a code (or a part of a code)"))
        return data


class VacantCourseGetTutorAttributionSerializer(serializers.Serializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    function = serializers.CharField(read_only=True, source="function.name")
    function_text = serializers.CharField(read_only=True, source="function.value")
    lecturing_volume = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    practical_volume = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)


class VacantCourseGetSerializer(serializers.Serializer):
    code = serializers.CharField(required=False, read_only=True)
    year = serializers.IntegerField(required=False, read_only=True)
    lecturing_volume_total = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    practical_volume_total = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    lecturing_volume_available = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    practical_volume_available = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    title = serializers.CharField(required=False, read_only=True)
    vacant_declaration_type = serializers.CharField(
        required=False, read_only=True, source="vacant_declaration_type.name"
    )
    vacant_declaration_type_text = serializers.CharField(source='vacant_declaration_type.value', read_only=True)
    is_in_team = serializers.BooleanField(required=False, read_only=True)
    allocation_entity = serializers.CharField(required=False, read_only=True, source="allocation_entity.code")
    tutors = VacantCourseGetTutorAttributionSerializer(read_only=True, many=True, default=list())
