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
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from backoffice.settings.rest_framework.common_views import LanguageContextSerializerMixin
from base.models.enums import education_group_categories
from education_group.api.serializers.education_group_title import EducationGroupTitleSerializer
from education_group.api.serializers.training import TrainingListSerializer, TrainingDetailSerializer
from education_group.api.views import utils
from program_management.models.education_group_version import EducationGroupVersion


class TrainingFilter(filters.FilterSet):
    from_year = filters.NumberFilter(field_name="offer__academic_year__year", lookup_expr='gte')
    to_year = filters.NumberFilter(field_name="offer__academic_year__year", lookup_expr='lte')
    in_type = filters.CharFilter(field_name="offer__education_group_type__name", lookup_expr='contains')
    version_type = filters.CharFilter(method='filter_version_type')
    acronym = filters.CharFilter(field_name="offer__acronym")
    partial_acronym = filters.CharFilter(field_name="root_group__partial_acronym")
    title = filters.CharFilter(field_name="offer__title")
    title_english = filters.CharFilter(field_name="offer__title_english")
    ares_ability = filters.NumberFilter(field_name="offer__hops__ares_ability")
    year = filters.NumberFilter(field_name="offer__academic_year__year")

    class Meta:
        model = EducationGroupVersion
        fields = ['acronym', 'partial_acronym', 'title', 'title_english', 'from_year', 'to_year']

    @staticmethod
    def filter_version_type(queryset, name, value):
        return utils.filter_version_type(queryset, value)


class TrainingList(LanguageContextSerializerMixin, generics.ListAPIView):
    """
       Return a list of all the training with optional filtering.
    """
    name = 'training-list'
    queryset = EducationGroupVersion.objects.filter(
        offer__education_group_type__category=education_group_categories.TRAINING
    ).select_related(
        'offer__education_group_type',
        'offer__academic_year'
    ).prefetch_related(
        'offer__administration_entity__entityversion_set',
        'offer__management_entity__entityversion_set'
    ).exclude(
        offer__acronym__icontains='common'
    )
    serializer_class = TrainingListSerializer
    filterset_class = TrainingFilter
    search_fields = (
        'offer__acronym',
        'root_group__partial_acronym',
        'offer__title',
        'offer__title_english',
    )
    ordering_fields = (
        'offer__acronym',
        'root_group__partial_acronym',
        'offer__title',
        'offer__title_english',
    )
    ordering = (
        '-offer__academic_year__year',
        'offer__acronym',
    )  # Default ordering


class TrainingDetail(LanguageContextSerializerMixin, generics.RetrieveAPIView):
    """
        Return the detail of the training
    """
    name = 'training_read'
    serializer_class = TrainingDetailSerializer
    pagination_class = None
    filter_backends = ()

    def get_object(self):
        acronym = self.kwargs['acronym']
        year = self.kwargs['year']
        version_name = self.kwargs.get('version_name', '')
        egv = get_object_or_404(
            EducationGroupVersion.objects.filter(
                offer__education_group_type__category=education_group_categories.TRAINING
            ).select_related(
                'offer__education_group_type',
                'offer__academic_year',
                'offer__main_teaching_campus',
                'offer__enrollment_campus',
                'offer__primary_language',
            ).prefetch_related(
                'offer__administration_entity__entityversion_set',
                'offer__management_entity__entityversion_set',
            ),
            offer__acronym__iexact=acronym,
            offer__academic_year__year=year,
            version_name=version_name,
            is_transition=False
        )
        return egv


class TrainingTitle(LanguageContextSerializerMixin, generics.RetrieveAPIView):
    """
        Return the title of the training
    """
    name = 'trainingstitle_read'
    serializer_class = EducationGroupTitleSerializer

    def get_object(self):
        acronym = self.kwargs['acronym']
        year = self.kwargs['year']
        egv = get_object_or_404(
            EducationGroupVersion.objects.all().select_related(
                'offer__academic_year',
            ),
            offer__acronym__iexact=acronym,
            offer__academic_year__year=year
        )
        return egv
