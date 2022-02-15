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
import functools
import operator
from typing import List

from dal import autocomplete
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
from base.views.learning_units.search.common import SearchTypes
from ddd.logic.shared_kernel.academic_year.commands import SearchAcademicYearCommand
from education_group.calendar.education_group_switch_calendar import EducationGroupSwitchCalendar
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear

COMMON_ORDERING_FIELDS = (
    ('academic_year__year', 'academic_year'), ('acronym', 'acronym'), ('full_title', 'title'),
    ('type_ordering', 'type'), ('subtype', 'subtype'),
    ('entity_requirement', 'requirement_entity'), ('entity_allocation', 'allocation_entity'),
    ('credits', 'credits'), ('status', 'status'), ('has_proposal', 'has_proposal'),
)

MOBILITY = 'mobility'
MOBILITY_CHOICE = ((MOBILITY, _('Mobility')),)


class LearningUnitFilter(FilterSet):
    academic_year__year = filters.ChoiceFilter(
        required=False,
        label=_('Ac yr.'),
        empty_label=pgettext_lazy("female plural", "All"),
    )
    acronym = filters.CharFilter(
        field_name="acronym",
        method="filter_learning_unit_year_field",
        max_length=40,
        required=False,
        label=_('Code'),
    )
    requirement_entity = filters.CharFilter(
        method='filter_entity',
        max_length=20,
        label=_('Req.Entity'),
    )
    allocation_entity = filters.CharFilter(
        method='filter_entity',
        max_length=20,
        label=_('Alloc.Entity'),
    )
    with_entity_subordinated = filters.BooleanFilter(
        method=lambda queryset, *args, **kwargs: queryset,
        label=_('Include subordinate entities'),
        widget=forms.CheckboxInput,
        initial='True'
    )
    tutor = filters.CharFilter(
        method="filter_tutor",
        max_length=40,
        label=_('Tutor'),
    )
    quadrimester = filters.ChoiceFilter(
        choices=quadrimesters.LearningUnitYearQuadrimester.choices(),
        required=False,
        field_name="quadrimester",
        label=_('Quadri'),
        empty_label=pgettext_lazy("male plural", "All"),
    )

    container_type = filters.MultipleChoiceFilter(
        choices=LearningContainerYearType.choices() + MOBILITY_CHOICE,
        required=False,
        field_name="learning_container_year__container_type",
        label=_('Type'),
        method="filter_container_type",
        widget=autocomplete.Select2Multiple(
            url='learning_unit_type_autocomplete',
            forward=None,
        ),
    )
    subtype = filters.ChoiceFilter(
        choices=learning_unit_year_subtypes.LEARNING_UNIT_YEAR_SUBTYPES,
        required=False,
        field_name="subtype",
        label=_('Subtype'),
        empty_label=pgettext_lazy("male plural", "All")
    )
    status = filters.ChoiceFilter(
        choices=active_status.ACTIVE_STATUS_LIST_FOR_FILTER,
        required=False,
        label=_('Status'),
        field_name="status",
        empty_label=pgettext_lazy("male plural", "All")
    )
    title = filters.CharFilter(
        field_name="full_title",
        method="filter_learning_unit_year_field",
        max_length=40,
        label=_('Title'),
    )
    search_type = filters.CharFilter(
        field_name="acronym",
        method=lambda request, *args, **kwargs: request,
        widget=forms.HiddenInput,
        required=False,
        initial=SearchTypes.SIMPLE_SEARCH.value,
        label=_('Search type')
    )

    with_only_proposals = filters.BooleanFilter(
        method="filter_only_proposals",
        label=_('Only UE in proposal'),
        widget=forms.CheckboxInput,
        initial=False
    )
    campus = filters.ModelChoiceFilter(
        queryset=find_main_campuses(),
        required=False,
        label=_('Learning location'),
        empty_label=_("All"),
    )
    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            COMMON_ORDERING_FIELDS
        ),
        widget=forms.HiddenInput
    )

    only_ue_having_classes = filters.BooleanFilter(
        method="filter_only_ue_with_classes",
        label=_('Only UE with classes'),
        widget=forms.CheckboxInput,
        initial=False
    )

    class Meta:
        model = LearningUnitYear
        fields = [
            "academic_year__year",
            "acronym",
            "title",
            "container_type",
            "subtype",
            "requirement_entity",
            "allocation_entity",
            "credits",
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_academic_year_field()
        self.queryset = self.get_queryset()

    def __init_academic_year_field(self):
        all_academic_year = message_bus_instance.invoke(SearchAcademicYearCommand(year=MINIMUM_LUE_YEAR))
        choices = [(ac_year.year, str(ac_year)) for ac_year in all_academic_year]
        self.form.fields['academic_year__year'].choices = choices
        self.form.fields['academic_year__year'].initial = EducationGroupSwitchCalendar().get_target_years_opened()

    def filter_tutor(self, queryset, name, value):
        value = value.replace(' ', '\\s')
        search_value = espace_special_characters(value)
        for tutor_name in search_value.split():
            queryset = queryset.filter(
                Q(learning_container_year__attributionnew__tutor__person__first_name__iregex=tutor_name
                  ) |
                Q(learning_container_year__attributionnew__tutor__person__last_name__iregex=tutor_name)
            ).distinct()
        return queryset

    def filter_container_type(self, queryset, name: str, selected_types: List[str]):
        if not selected_types:
            return queryset

        selected_types_without_mobility_and_external = [
            type
            for type in selected_types
            if type not in (MOBILITY, learning_container_year_types.EXTERNAL)
        ]

        filter_clauses = Q(learning_container_year__container_type__in=selected_types_without_mobility_and_external)
        if MOBILITY in selected_types:
            filter_clauses = filter_clauses | Q(externallearningunityear__mobility=True)
        if learning_container_year_types.EXTERNAL in selected_types:
            filter_clauses = filter_clauses | Q(externallearningunityear__co_graduation=True)

        return queryset.filter(filter_clauses)

    def filter_entity(self, queryset, name, value):
        return filter_by_entities(name,
                                  queryset,
                                  espace_special_characters(value),
                                  self.form.cleaned_data['with_entity_subordinated'])

    def get_queryset(self):
        # Need this close so as to return empty query by default when form is unbound
        if not self.data:
            return LearningUnitYear.objects.none()

        has_proposal = ProposalLearningUnit.objects.filter(
            learning_unit_year=OuterRef('pk'),
        )
        has_classes = LearningClassYear.objects.filter(
            learning_component_year__learning_unit_year=OuterRef('pk'),
        )
        queryset = LearningUnitYear.objects_with_container.select_related(
            'academic_year',
            'learning_container_year__academic_year',
            'language',
            'proposallearningunit',
            'externallearningunityear'
        ).order_by('academic_year__year', 'acronym').annotate(
            has_proposal=Exists(has_proposal),
            has_classes=Exists(has_classes)
        )
        queryset = LearningUnitYearQuerySet.annotate_full_title_class_method(queryset)
        queryset = LearningUnitYearQuerySet.annotate_entities_allocation_and_requirement_acronym(queryset)

        queryset = queryset.annotate(
            type_ordering=Case(
                When(externallearningunityear__mobility=True, then=Value(str(_('Mobility')))),
                *[When(learning_container_year__container_type=key, then=Value(str(_(val))))
                  for i, (key, val) in enumerate(LearningContainerYearType.choices())],
                default=Value(''),
                output_field=CharField()
            )
        )
        return queryset

    def filter_learning_unit_year_field(self, queryset, name, value):
        return filter_field_by_regex(queryset, name, value)

    def filter_only_proposals(self, queryset, name, value):
        if value:
            return queryset.filter(has_proposal=True)
        return queryset

    def filter_only_ue_with_classes(self, queryset, name, value):
        if value:
            return queryset.filter(has_classes=True)
        return queryset


def filter_by_entities(name, queryset, value, with_subordinated):
    lookup_expression = "__".join(["learning_container_year", name, "in"])
    if value:
        entity_ids = get_entities_ids(value, with_subordinated)
        queryset = queryset.filter(**{lookup_expression: entity_ids})
    return queryset
