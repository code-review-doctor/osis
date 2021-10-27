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
from django.db.models import Case, When, Q, F, Value, CharField
from django.db.models.functions import Replace, Concat, Lower, Substr
from django.utils.functional import cached_property
from django_filters import rest_framework as filters
from rest_framework import generics

from backoffice.settings.rest_framework.common_views import LanguageContextSerializerMixin
from base.models.enums import offer_enrollment_state
from base.models.offer_enrollment import OfferEnrollment
from base.models.person import Person
from education_group.models.enums.cohort_name import CohortName
from offer_enrollment.api.serializers.enrollment import EnrollmentSerializer

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class OfferEnrollmentFilter(filters.FilterSet):
    enrollment_state = filters.MultipleChoiceFilter(
        field_name='enrollment_state',
        choices=offer_enrollment_state.STATES
    )
    year = filters.NumberFilter(field_name="education_group_year__academic_year__year")


class OfferEnrollmentsListView(LanguageContextSerializerMixin, generics.ListAPIView):
    """
       Return all offer enrollments of a specified user by global id
    """
    name = 'enrollments'
    serializer_class = EnrollmentSerializer
    ordering = ['-education_group_year__academic_year__year']
    filterset_class = OfferEnrollmentFilter

    def get_queryset(self):
        qs = self.get_common_queryset().filter(
            student__registration_id=self.kwargs['registration_id']
        )
        return self.annotate_queryset(qs)

    @staticmethod
    def get_common_queryset():
        return OfferEnrollment.objects.all().select_related(
            'student__person',
            'education_group_year__academic_year',
            'cohort_year__education_group_year__academic_year'
        )

    @staticmethod
    def annotate_queryset(qs):
        return qs.annotate(
            acronym=Case(
                When(
                    Q(cohort_year__name=CohortName.FIRST_YEAR.name),
                    then=Replace('cohort_year__education_group_year__acronym', Value('1'), Value('11'))
                ),
                default=F('education_group_year__acronym'),
                output_field=CharField()
            ),
            year=F('education_group_year__academic_year__year'),
            title_fr=Case(
                When(
                    Q(cohort_year__name=CohortName.FIRST_YEAR.name),
                    then=Concat(
                        Value('Première année de '),
                        Lower(Substr('education_group_year__title', 1, 1)),
                        Substr('education_group_year__title', 2)
                    )
                ),
                default=F('education_group_year__title'),
                output_field=CharField()
            ),
            title_en=Case(
                When(
                    Q(cohort_year__name=CohortName.FIRST_YEAR.name) &
                    Q(education_group_year__title_english__isnull=False) &
                    ~Q(education_group_year__title_english=''),
                    then=Concat(
                        Value('First year of '),
                        Lower(Substr('education_group_year__title_english', 1, 1)),
                        Substr('education_group_year__title_english', 2)
                    )
                ),
                default=F('education_group_year__title_english'),
                output_field=CharField()
            ),
        )


class MyOfferEnrollmentsListView(OfferEnrollmentsListView):
    """
       Return all offer enrollments of connected user
    """
    name = 'my_enrollments'

    def get_queryset(self):
        qs = self.get_common_queryset().filter(
            student__person=self.person
        )
        return self.annotate_queryset(qs)

    @cached_property
    def person(self) -> Person:
        return self.request.user.person


class MyOfferYearEnrollmentsListView(MyOfferEnrollmentsListView):
    """
       Return all offer enrollments of connected user for a specific year
    """
    name = 'my_enrollments_year'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            education_group_year__academic_year__year=self.kwargs['year']
        )
