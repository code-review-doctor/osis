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
    subtype_sport = serializers.CharField()
    subtype_sport_text = serializers.SerializerMethodField()
    subtype_disability = serializers.CharField()
    subtype_disability_text = serializers.SerializerMethodField()
    guide = serializers.CharField()
    arrangement_additional_time = serializers.BooleanField()
    arrangement_appropriate_copy = serializers.BooleanField()
    arrangement_other = serializers.BooleanField()
    arrangement_specific_locale = serializers.BooleanField()
    arrangement_comment = serializers.CharField()

    def get_type_text(self, obj):
        return PepsTypes.get_value(obj.type)

    def get_subtype_sport_text(self, obj):
        return SportSubtypes.get_value(obj.subtype_sport)

    def get_subtype_disability_text(self, obj):
        return HtmSubtypes.get_value(obj.subtype_disability)
