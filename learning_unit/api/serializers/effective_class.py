##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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


class EffectiveClassSerializer(serializers.Serializer):
    class_code = serializers.CharField()
    title_fr = serializers.CharField()
    title_en = serializers.CharField()
    teaching_place_uuid = serializers.CharField()
    campus_name = serializers.CharField()
    organization_name = serializers.CharField()
    derogation_quadrimester = serializers.CharField()
    session_derogation = serializers.CharField()
    volume_q1 = serializers.DecimalField(max_digits=5, decimal_places=2)
    volume_q2 = serializers.DecimalField(max_digits=5, decimal_places=2)
    class_type = serializers.CharField()
