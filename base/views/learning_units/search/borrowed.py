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
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django_filters.views import FilterView

from base.business.learning_units.xls_comparison import get_academic_year_of_reference
from base.forms.learning_unit.comparison import SelectComparisonYears
from base.forms.learning_unit.search_form import LearningUnitFilter
from base.models.academic_year import starting_academic_year
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import CacheFilterMixin
from base.views.learning_units.search.common import BORROWED_COURSE, ITEMS_PER_PAGES, SerializeFilterListIfAjaxMixin
from learning_unit.api.serializers.learning_unit import LearningUnitSerializer


# TODO adapt filter to borrowed course
# TODO excel for borrowed course
class BorrowedLearningUnitSearch(PermissionRequiredMixin, CacheFilterMixin, SerializeFilterListIfAjaxMixin, FilterView):
    model = LearningUnitYear
    template_name = "learning_unit/search/service_course.html"
    raise_exception = True
    search_type = BORROWED_COURSE

    filterset_class = LearningUnitFilter
    permission_required = 'base.can_access_learningunit'
    cache_exclude_params = 'xls_status'

    serializer_class = LearningUnitSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        starting_ac = starting_academic_year()

        context.update({
            'form': context['filter'].form,
            'learning_units_count': context["paginator"].count,
            'current_academic_year': starting_ac,
            'proposal_academic_year': starting_ac.next(),
            'search_type': self.search_type,
            'page_obj': context["page_obj"],
            'items_per_page': context["paginator"].per_page,
            "form_comparison": SelectComparisonYears(
                academic_year=get_academic_year_of_reference(context['object_list'])
            ),
        })
        return context

    def get_paginate_by(self, queryset):
        return self.request.GET.get("paginator_size", ITEMS_PER_PAGES)

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            serializer = LearningUnitSerializer(context["page_obj"], context={'request': self.request}, many=True)
            return JsonResponse({'object_list': serializer.data})
        return super().render_to_response(context, **response_kwargs)
