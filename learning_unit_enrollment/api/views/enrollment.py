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
from django.db.models import Case, When, Q, F
from django.db.models.functions import Concat
from rest_framework import generics

from base.models.learning_unit_enrollment import LearningUnitEnrollment
from learning_unit_enrollment.api.serializers.enrollment import EnrollmentSerializer

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class LearningUnitEnrollmentsListView(generics.ListAPIView):
    """
       Return all enrollments of a learning unit year
    """
    name = 'enrollments'
    serializer_class = EnrollmentSerializer
    search_fields = ['student_first_name', 'student_last_name']

    def get_queryset(self):
        acronym = self.kwargs['acronym']
        year = self.kwargs['year']
        qs = LearningUnitEnrollment.objects.annotate(
            learning_unit_academic_year=F('learning_unit_year__academic_year__year'),
            learning_unit_acronym=Case(
                When(
                    Q(learning_class_year__isnull=False),
                    then=Concat(F('learning_unit_year__acronym'), F('learning_class_year__acronym'))
                ),
                default=F('learning_unit_year__acronym')
            )
        ).filter(
            learning_unit_acronym=acronym,
            learning_unit_academic_year=year
        ).annotate(
            student_last_name=F('offer_enrollment__student__person__last_name'),
            student_first_name=F('offer_enrollment__student__person__first_name'),
            student_email=F('offer_enrollment__student__person__email'),
            student_registration_id=F('offer_enrollment__student__registration_id'),
            program=F('offer_enrollment__education_group_year__acronym'),
        ).select_related(
            'offer_enrollment__student__studentspecificprofile',
            'offer_enrollment__student__person',
            'learning_unit_year__academic_year'
        )
        if self.request.GET.get('ordering') == 'specific_profile':
            qs = qs.order_by('offer_enrollment__student__studentspecificprofile')
        if self.request.GET.get('ordering') == '-specific_profile':
            qs = qs.order_by('-offer_enrollment__student__studentspecificprofile')
        return qs
