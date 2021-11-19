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
import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from base.models.student import Student


class StudentFilter(django_filters.FilterSet):
    registration_id = django_filters.CharFilter(
        max_length=10,
        required=False,
        label=_('Registration Id'),
        field_name='registration_id'
    )
    name = django_filters.CharFilter(max_length=20, required=False, label=_('Name'), method='filter_name')

    def filter_name(self, queryset, name, value):
        for word in value.split():
            queryset = queryset.filter(Q(person__first_name__icontains=word) | Q(person__last_name__icontains=word))
        return queryset

    class Meta:
        model = Student
        fields = ['registration_id', 'person']

    def __init__(self, *args, **kwargs):
        super(StudentFilter, self).__init__(*args, **kwargs)

        if self.data == {}:
            self.queryset = self.queryset.none()

    def filter_queryset(self, queryset):
        if self.form.cleaned_data["registration_id"] or self.form.cleaned_data["name"]:
            queryset = super().filter_queryset(queryset)
            return queryset.select_related('person')
        return Student.objects.none()
