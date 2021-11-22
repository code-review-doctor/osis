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

import logging

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django_filters.views import FilterView

from base.forms.entity import EntityVersionFilter, EntityListSerializer
from base.models.entity_version import EntityVersion
from base.utils.search import SearchMixin
from django.contrib.auth.mixins import LoginRequiredMixin
logger = logging.getLogger(settings.DEFAULT_LOGGER)


class EntitySearch(LoginRequiredMixin, SearchMixin, FilterView):
    model = EntityVersion
    paginate_by = 25
    template_name = "entities.html"
    raise_exception = True
    paginate_by = 25
    filterset_class = EntityVersionFilter
    ordering = ['acronym']

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            serializer = EntityListSerializer(context['object_list'], many=True)
            return JsonResponse({'object_list': serializer.data})
        return super().render_to_response(context, **response_kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.select_related('entity__organization').order_by('acronym')

