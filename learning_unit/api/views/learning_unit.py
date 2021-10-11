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
from django.db.models import OuterRef, Exists
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters, Filter
from rest_framework import generics

from backoffice.settings.rest_framework.common_views import LanguageContextSerializerMixin
from base.models.learning_unit_year import LearningUnitYear, LearningUnitYearQuerySet
from learning_unit.api.serializers.learning_unit import LearningUnitDetailedSerializer, LearningUnitSerializer, \
    LearningUnitTitleSerializer, ExternalLearningUnitDetailedSerializer
from learning_unit.models.learning_class_year import LearningClassYear


def annotate_has_classes(queryset):
    queryset = queryset.annotate(has_classes=Exists(
        LearningClassYear.objects.filter(
            learning_component_year__learning_unit_year=OuterRef('id')
        )
    ))
    return queryset


class ListFilter(Filter):
    def filter(self, qs, value):
        if not value:
            return qs

        self.lookup_expr = 'in'
        values = value.split(',')
        return super(ListFilter, self).filter(qs, values)


class LearningUnitFilter(filters.FilterSet):
    learning_unit_codes = ListFilter(field_name='acronym', lookup_expr="icontains")
    acronym_like = filters.CharFilter(field_name='acronym', lookup_expr='icontains')
    year = filters.NumberFilter(field_name="academic_year__year")
    campus = filters.CharFilter(field_name='campus__name', lookup_expr='icontains')
    stage_dimona = filters.BooleanFilter(field_name='stage_dimona')

    class Meta:
        model = LearningUnitYear
        fields = ['acronym', 'acronym_like', 'year', 'stage_dimona']


class LearningUnitList(LanguageContextSerializerMixin, generics.ListAPIView):
    """
       Return a list of all the learning unit with optional filtering.
    """
    name = 'learningunits_list'
    queryset = LearningUnitYear.objects.filter(
    ).select_related(
        'academic_year',
        'learning_container_year'
    ).prefetch_related(
        'learning_container_year__requirement_entity__entityversion_set',
    ).annotate_full_title()
    queryset = annotate_has_classes(queryset)

    serializer_class = LearningUnitSerializer
    filterset_class = LearningUnitFilter
    search_fields = None
    ordering_fields = None
    ordering = (
        '-academic_year__year',
        'acronym',
    )  # Default ordering


class LearningUnitDetailed(LanguageContextSerializerMixin, generics.RetrieveAPIView):
    """
        Return the detail of the learning unit
    """
    name = 'learningunits_read'

    def get_object(self):
        acronym = self.kwargs['acronym']
        year = self.kwargs['year']
        queryset = LearningUnitYear.objects.filter(learning_container_year__isnull=False).select_related(
            'language',
            'campus',
            'academic_year',
            'learning_container_year',
            'externallearningunityear'
        ).prefetch_related(
            'learning_container_year__requirement_entity__entityversion_set',
            'learningcomponentyear_set',
        ).annotate_full_title()
        queryset = annotate_has_classes(queryset)
        luy = get_object_or_404(
            LearningUnitYearQuerySet.annotate_entities_allocation_and_requirement_acronym(queryset),
            acronym__iexact=acronym,
            academic_year__year=year
        )
        return luy

    def get_serializer_class(self):
        if self.get_object().is_external():
            return ExternalLearningUnitDetailedSerializer
        return LearningUnitDetailedSerializer


class LearningUnitTitle(LanguageContextSerializerMixin, generics.RetrieveAPIView):
    """
        Return the title of the learning unit
    """
    name = 'learningunitstitle_read'
    serializer_class = LearningUnitTitleSerializer

    def get_object(self):
        acronym = self.kwargs['acronym']
        year = self.kwargs['year']
        luy = get_object_or_404(
            LearningUnitYear.objects.all().select_related(
                'academic_year',
            ).annotate_full_title(),
            acronym__iexact=acronym,
            academic_year__year=year
        )
        return luy
