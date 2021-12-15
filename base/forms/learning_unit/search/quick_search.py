# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from django import forms
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django_filters import FilterSet, filters, OrderingFilter

from backoffice.settings.base import MINIMUM_LUE_YEAR
from base.models.learning_unit_year import LearningUnitYear, LearningUnitYearQuerySet
from ddd.logic.shared_kernel.academic_year.commands import SearchAcademicYearCommand
from infrastructure.messages_bus import message_bus_instance


class QuickLearningUnitYearFilter(FilterSet):
    academic_year__year = filters.ChoiceFilter(
        required=False,
        label=_('Ac yr.'),
        empty_label=pgettext_lazy("female plural", "All"),
    )
    acronym = filters.CharFilter(
        field_name="acronym",
        lookup_expr="iregex",
        max_length=40,
        required=False,
        label=_('Code'),
    )
    title = filters.CharFilter(
        field_name="full_title",
        lookup_expr="icontains",
        max_length=40,
        label=_('Title'),
    )

    ordering = OrderingFilter(
        fields=(
            ('academic_year__year', 'academic_year'),
            ('acronym', 'acronym'),
            ('full_title', 'title'),
        ),
        widget=forms.HiddenInput
    )

    class Meta:
        model = LearningUnitYear
        fields = [
            "academic_year__year",
            "acronym",
            "title",
        ]

    def __init__(self, *args, initial=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_academic_year_field()
        self.queryset = self.get_queryset()
        if initial:
            self.form.fields["academic_year__year"].initial = initial["academic_year__year"]

    def __init_academic_year_field(self):
        all_academic_year = message_bus_instance.invoke(SearchAcademicYearCommand(year=MINIMUM_LUE_YEAR))
        choices = [(ac_year.year, str(ac_year)) for ac_year in all_academic_year]
        self.form.fields['academic_year__year'].choices = choices

    def get_queryset(self):
        # Need this close so as to return empty query by default when form is unbound
        # 'changed_data' has been used instead of 'has_changed' here because the hidden field 'academic_year'
        # which never is empty so need to check the 2 other fields of the form
        watched_form_fields = ['acronym', 'title']
        if not self.data or not any(field in self.form.changed_data for field in watched_form_fields):
            return LearningUnitYear.objects.none()
        queryset = LearningUnitYear.objects_with_container.select_related(
            'academic_year',
        )
        queryset = LearningUnitYearQuerySet.annotate_full_title_class_method(queryset)
        return queryset
