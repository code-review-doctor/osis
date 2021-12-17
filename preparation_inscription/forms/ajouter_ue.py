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
from django import forms
from django.core.exceptions import ValidationError

from base.forms.utils.datefield import DatePickerInput
from django.utils.translation import gettext_lazy as _
from django import forms
from django.db.models import Q, OuterRef, Exists, Case, When, Value, CharField
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django_filters import FilterSet, filters, OrderingFilter

from backoffice.settings.base import MINIMUM_LUE_YEAR
from base.business.entity import get_entities_ids
from base.forms.utils.filter_field import filter_field_by_regex, espace_special_characters
from base.models.campus import find_main_campuses
from base.models.enums import quadrimesters, learning_unit_year_subtypes, active_status, learning_container_year_types
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.learning_unit_year import LearningUnitYear, LearningUnitYearQuerySet
from base.models.proposal_learning_unit import ProposalLearningUnit
from base.views.learning_units.search.common import SearchTypes, BaseLearningUnitSearch
from ddd.logic.shared_kernel.academic_year.commands import SearchAcademicYearCommand
from education_group.calendar.education_group_switch_calendar import EducationGroupSwitchCalendar
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear

from base.forms.learning_unit.comparison import SelectComparisonYears
from base.forms.learning_unit.search.simple import LearningUnitFilter
from base.utils.search import RenderToExcel
from base.views.learning_units.search.common import _create_xls, _create_xls_comparison, \
    _create_xls_attributions, _create_xls_with_parameters, \
    BaseLearningUnitSearch, _create_xls_educational_specifications, SearchTypes, \
    _create_xls_ue_utilizations_with_one_training_per_line
from learning_unit.api.serializers.learning_unit import LearningUnitSerializer


class LearningUnitSearch(BaseLearningUnitSearch):
    template_name = "onglets.html"
    search_type = SearchTypes.SIMPLE_SEARCH
    filterset_class = LearningUnitFilter
    serializer_class = LearningUnitSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = context["form"]

        return context
# class AjouterUeForm(forms.form):
#     pass
#
#
# class AjouterUeFilter(FilterSet):
#     academic_year__year = filters.ChoiceFilter(
#         required=False,
#         label=_('Ac yr.'),
#         empty_label=pgettext_lazy("female plural", "All"),
#     )
#     acronym = filters.CharFilter(
#         field_name="acronym",
#         method="filter_learning_unit_year_field",
#         max_length=40,
#         required=False,
#         label=_('Code'),
#     )
#     title = filters.CharFilter(
#         field_name="full_title",
#         method="filter_learning_unit_year_field",
#         max_length=40,
#         label=_('Title'),
#     )
