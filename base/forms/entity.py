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
import django_filters
from django.forms import TextInput
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from base.models.entity_version import EntityVersion


class EntityVersionFilter(django_filters.FilterSet):
    acronym = django_filters.CharFilter(
        lookup_expr='icontains', label=_("Acronym"),
        widget=TextInput(attrs={'style': "text-transform:uppercase"})
    )
    title = django_filters.CharFilter(lookup_expr='icontains', label=_("Title"), )

    class Meta:
        model = EntityVersion
        fields = ["entity_type"]


class EntityListSerializer(serializers.Serializer):
    acronym = serializers.CharField()
    title = serializers.CharField()
    entity_type = serializers.CharField()
    # Display human readable value
    entity_type_text = serializers.CharField(source='get_entity_type_display', read_only=True)
    organization = serializers.SerializerMethodField()
    select_url = serializers.SerializerMethodField()

    def get_organization(self, obj):
        return str(obj.entity.organization)

    def get_select_url(self, obj):
        return reverse(
            "entity_read",
            kwargs={'entity_version_id': obj.id}
        )
