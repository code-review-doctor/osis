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
from django.db.models.functions import Concat, Replace
from django.utils.functional import cached_property
from rest_framework import generics

from base.models.enums.offer_enrollment_state import SUBSCRIBED, PROVISORY
from base.models.learning_unit_enrollment import LearningUnitEnrollment
from base.models.person import Person
from education_group.models.enums.cohort_name import CohortName
from learning_unit_enrollment.api.serializers.enrollment import EnrollmentSerializer

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class LearningUnitEnrollmentsListView(generics.ListAPIView):
    """
       Return all enrollments in valid state of a learning unit year
    """
    name = 'enrollments'
    serializer_class = EnrollmentSerializer
    search_fields = ['student_first_name', 'student_last_name']
    ordering_fields = [
        'student_last_name',
        'student_first_name',
        'student_registration_id',
        'student_email',
        'specific_profile',
        'program'
    ]

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data.update({'enrolled_students_count': self.get_queryset().count()})
        return response

    @property
    def year(self):
        return self.kwargs['year']

    def get_queryset(self):
        return LearningUnitEnrollment.objects.filter(
            learning_unit_year__academic_year__year=self.year,
            learning_unit_year__acronym__contains=self.kwargs['acronym'][:-1],
            offer_enrollment__enrollment_state__in=[SUBSCRIBED, PROVISORY]
        ).annotate(
            learning_unit_academic_year=F('learning_unit_year__academic_year__year'),
            learning_unit_acronym=Case(
                When(
                    Q(learning_class_year__isnull=False),
                    then=Concat(F('learning_unit_year__acronym'), F('learning_class_year__acronym'))
                ),
                default=F('learning_unit_year__acronym')
            )
        ).filter(
            learning_unit_acronym=self.kwargs['acronym'],
        ).annotate(
            student_last_name=F('offer_enrollment__student__person__last_name'),
            student_first_name=F('offer_enrollment__student__person__first_name'),
            student_email=F('offer_enrollment__student__person__email'),
            student_registration_id=F('offer_enrollment__student__registration_id'),
            program=Case(
                When(
                    Q(offer_enrollment__cohort_year__name=CohortName.FIRST_YEAR.name),
                    then=Replace(
                        'offer_enrollment__cohort_year__education_group_year__acronym', Value('1'), Value('11')
                    )
                ),
                default=F('offer_enrollment__education_group_year__acronym'),
                output_field=CharField()
            ),
            specific_profile=F('offer_enrollment__student__studentspecificprofile')
        ).select_related(
            'offer_enrollment__student__studentspecificprofile',
            'offer_enrollment__student__person',
            'offer_enrollment__education_group_year',
            'offer_enrollment__cohort_year__education_group_year',
            'learning_unit_year__academic_year',
        )


class MyLearningUnitEnrollmentsListView(LearningUnitEnrollmentsListView):
    """
       Return all enrollments of a the connected user based on an offer enrollment
    """
    name = 'my_enrollments'

    @cached_property
    def person(self) -> Person:
        return self.request.user.person

    def get_queryset(self):
        return LearningUnitEnrollment.objects.filter(
            offer_enrollment__student__person=self.person,
            learning_unit_year__academic_year__year=self.year,
            offer_enrollment__education_group_year__acronym=self.kwargs['program_code'].replace('11', '1')
        ).annotate(
            learning_unit_academic_year=F('learning_unit_year__academic_year__year'),
            learning_unit_acronym=Case(
                When(
                    Q(learning_class_year__isnull=False),
                    then=Concat(F('learning_unit_year__acronym'), F('learning_class_year__acronym'))
                ),
                default=F('learning_unit_year__acronym')
            )
        ).annotate(
            student_last_name=F('offer_enrollment__student__person__last_name'),
            student_first_name=F('offer_enrollment__student__person__first_name'),
            student_email=F('offer_enrollment__student__person__email'),
            student_registration_id=F('offer_enrollment__student__registration_id'),
            program=Case(
                When(
                    Q(offer_enrollment__cohort_year__name=CohortName.FIRST_YEAR.name),
                    then=Replace(
                        'offer_enrollment__cohort_year__education_group_year__acronym', Value('1'), Value('11')
                    )
                ),
                default=F('offer_enrollment__education_group_year__acronym'),
                output_field=CharField()
            ),
            specific_profile=F('offer_enrollment__student__studentspecificprofile')
        ).select_related(
            'offer_enrollment__student__studentspecificprofile',
            'offer_enrollment__student__person',
            'offer_enrollment__education_group_year',
            'offer_enrollment__cohort_year__education_group_year',
            'learning_unit_year__academic_year',
        )

