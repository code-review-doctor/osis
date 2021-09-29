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
from django.db.models.functions import Replace
from django.utils.functional import cached_property
from rest_framework import generics

from backoffice.settings.rest_framework.common_views import LanguageContextSerializerMixin
from base.models.offer_enrollment import OfferEnrollment
from base.models.person import Person
from education_group.models.enums.cohort_name import CohortName
from offer_enrollment.api.serializers.enrollment import EnrollmentSerializer

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class MyOfferEnrollmentsListView(LanguageContextSerializerMixin, generics.ListAPIView):
    """
       Return all offer enrollments of connected user
    """
    name = 'my_enrollments'
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return OfferEnrollment.objects.filter(student__person=self.person).select_related(
            'student__person',
            'education_group_year__academic_year',
            'cohort_year__education_group_year__academic_year'
        ).annotate(
            acronym=Case(
                When(
                    Q(cohort_year__name=CohortName.FIRST_YEAR.name),
                    then=Replace('cohort_year__education_group_year__acronym', Value('1'), Value('11'))
                ),
                default=F('education_group_year__acronym'),
                output_field=CharField()
            ),
            year=F('education_group_year__academic_year__year'),
            title_fr=F('education_group_year__title'),
            title_en=F('education_group_year__title_english')
        )

    @cached_property
    def person(self) -> Person:
        return self.request.user.person


class MyOfferYearEnrollmentsListView(MyOfferEnrollmentsListView):
    """
       Return all offer enrollments of connected user for a specific year
    """
    name = 'my_enrollments_year'
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            education_group_year__academic_year__year=self.kwargs['year']
        )
