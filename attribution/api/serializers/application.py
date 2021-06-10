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
from rest_framework import serializers


class ApplicationGetSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    code = serializers.CharField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    course_title = serializers.CharField(read_only=True)
    lecturing_volume = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    practical_volume = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    lecturing_volume_available = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    practical_volume_available = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    remark = serializers.CharField(read_only=True)
    course_summary = serializers.CharField(read_only=True)


class ApplicationPostSerializer(serializers.Serializer):
    code = serializers.CharField()
    lecturing_volume = serializers.DecimalField(max_digits=5, decimal_places=1)
    practical_volume = serializers.DecimalField(max_digits=5, decimal_places=1)
    remark = serializers.CharField(default='', allow_blank=True)
    course_summary = serializers.CharField(default='', allow_blank=True)


class ApplicationPutSerializer(serializers.Serializer):
    lecturing_volume = serializers.DecimalField(max_digits=5, decimal_places=1)
    practical_volume = serializers.DecimalField(max_digits=5, decimal_places=1)
    remark = serializers.CharField(default='', allow_blank=True)
    course_summary = serializers.CharField(default='', allow_blank=True)


class AttributionsAboutToExpireGetSerializer(serializers.Serializer):
    code = serializers.CharField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    lecturing_volume = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    practical_volume = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    function = serializers.CharField(read_only=True, source="function.name")
    function_text = serializers.CharField(read_only=True, source="function.value")
    end_year = serializers.IntegerField(read_only=True)
    start_year = serializers.IntegerField(read_only=True)
    total_lecturing_volume_course = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    total_practical_volume_course = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    lecturing_volume_available = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    practical_volume_available = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    unavailable_renewal_reason = serializers.CharField(default='', read_only=True)
    is_renewable = serializers.BooleanField(read_only=True)


class RenewAttributionAboutToExpirePostSerializer(serializers.Serializer):
    codes = serializers.ListField(child=serializers.CharField(), allow_empty=False)


class MyChargeSummarySerializer(serializers.Serializer):
    code = serializers.CharField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    start_year = serializers.IntegerField(read_only=True)
    end_year = serializers.IntegerField(read_only=True)
    function = serializers.CharField(read_only=True, source="function.name")
    function_text = serializers.CharField(read_only=True, source="function.value")
    lecturing_volume = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    lecturing_volume_available = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    practical_volume = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    practical_volume_available = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    total_lecturing_volume_course = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    total_practical_volume_course = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
