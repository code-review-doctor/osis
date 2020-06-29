##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
import itertools
from collections import OrderedDict

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.html import format_html

from base.business.education_group import create_xls, ORDER_COL, ORDER_DIRECTION, create_xls_administrative_data
from base.forms.search.search_form import get_research_criteria
from base.models.education_group_type import EducationGroupType


def _get_filter(form):
    return OrderedDict(itertools.chain(get_research_criteria(form)))


def _create_xls_administrative_data(view_obj, context, **response_kwargs):
    user = view_obj.request.user
    egys = context["filter"].qs
    filters = _get_filter(context["form"])
    # FIXME: use ordering args in filter_form! Remove xls_order_col/xls_order property
    order = {ORDER_COL: view_obj.request.GET.get('xls_order_col'),
             ORDER_DIRECTION: view_obj.request.GET.get('xls_order')}
    return create_xls_administrative_data(user, egys, filters, order)


class EducationGroupTypeAutoComplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return EducationGroupType.objects.none()

        qs = EducationGroupType.objects.all()

        category = self.forwarded.get('category', None)
        if category:
            qs = qs.filter(category=category)
        if self.q:
            # Filtering must be done in python because translated value.
            ids_to_keep = {result.pk for result in qs if self.q.lower() in result.get_name_display().lower()}
            qs = qs.filter(id__in=ids_to_keep)

        qs = qs.order_by_translated_name()
        return qs

    def get_result_label(self, result):
        return format_html('{}', result.get_name_display())
