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

from base.models.enums.peps_type import PepsTypes, SportSubtypes, HtmSubtypes


class StudentSpecificProfileSerializer(serializers.Serializer):
    type = serializers.CharField()
    type_text = serializers.SerializerMethodField()
    subtype = serializers.SerializerMethodField()
    subtype_text = serializers.SerializerMethodField()
    guide = serializers.CharField()
    arrangement_additional_time = serializers.BooleanField()
    arrangement_appropriate_copy = serializers.BooleanField()
    arrangement_other = serializers.BooleanField()
    arrangement_specific_locale = serializers.BooleanField()
    arrangement_comment = serializers.CharField()

    @staticmethod
    def get_type_text(obj):
        return PepsTypes.get_value(obj.type)

    @staticmethod
    def get_subtype(obj):
        if obj.type == PepsTypes.SPORT.name:
            return obj.subtype_sport
        elif obj.type == PepsTypes.DISABILITY.name:
            return obj.subtype_disability
        return ""

    @staticmethod
    def get_subtype_text(obj):
        if obj.type == PepsTypes.SPORT.name:
            return SportSubtypes.get_value(obj.subtype_sport)
        elif obj.type == PepsTypes.DISABILITY.name:
            return HtmSubtypes.get_value(obj.subtype_disability)
        return ""
