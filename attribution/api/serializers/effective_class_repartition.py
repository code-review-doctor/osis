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


class EffectiveClassRepartitionSerializer(serializers.Serializer):
    code = serializers.CharField()
    title_fr = serializers.CharField()
    title_en = serializers.CharField()
    schedule_url = serializers.SerializerMethodField()
    has_peps = serializers.BooleanField()

    def get_schedule_url(self, obj):
        year = self.context.get('year')
        has_access_schedule_calendar = year in self.context["access_schedule_calendar"].get_target_years_opened() \
            if "access_schedule_calendar" in self.context else False
        if settings.SCHEDULE_APP_URL and has_access_schedule_calendar:
            clean_code = obj.get('code').replace('_', '').replace('-', '')
            return settings.SCHEDULE_APP_URL.format(code=clean_code)
