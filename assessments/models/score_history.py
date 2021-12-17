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
import uuid

from django.contrib import admin
from osis_history import models as osis_history_models


SCORE_HISTORY_TAGS = ['encodage_de_notes']


class ScoreHistoryAdmin(admin.ModelAdmin):
    list_display = ('message_fr', 'message_en', 'author', 'created',)
    search_fields = ['author', 'message_fr', 'message_en', ]
    list_display_links = None
    actions = None
    change_list_template = "assessments/admin/score_history_list.html"

    def get_queryset(self, request):
        return super().get_queryset(request).filter(tags__contains=SCORE_HISTORY_TAGS)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            uuid_from_str = uuid.uuid3(uuid.NAMESPACE_OID, name=search_term)
            queryset |= self.model.objects.filter(object_uuid=uuid_from_str)
        return queryset, use_distinct


class ScoreHistory(osis_history_models.HistoryEntry):
    class Meta:
        proxy = True
