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
from django.conf import settings
from rest_framework import serializers

from attribution.models.enums.function import Functions


class AttributionSerializer(serializers.Serializer):
    code = serializers.CharField()
    title_fr = serializers.CharField()
    title_en = serializers.CharField()
    year = serializers.IntegerField()
    credits = serializers.DecimalField(max_digits=5, decimal_places=2)
    start_year = serializers.IntegerField()
    function = serializers.CharField()
    function_text = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()

    def get_function_text(self, obj) -> str:
        if obj.function:
            return Functions.get_value(obj.function)
        return ""

    def get_links(self, obj) -> dict:
        return {
            "catalog": self.__get_catalog_url(obj),
            "schedule": self.__get_schedule_url(obj)
        }

    def __get_catalog_url(self, obj):
        if settings.LEARNING_UNIT_PORTAL_URL:
            return settings.LEARNING_UNIT_PORTAL_URL.format(year=obj.year, code=obj.code)

    def __get_schedule_url(self, obj):
        if settings.SCHEDULE_APP_URL and "access_schedule_calendar" in self.context and \
                obj.year in self.context["access_schedule_calendar"].get_target_years_opened():
            return settings.SCHEDULE_APP_URL.format(code=obj.code)
