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

    def get_queryset(self):
        acronym = self.kwargs['acronym']
        year = self.kwargs['year']
        return LearningUnitEnrollment.objects.filter(
            learning_unit_year__acronym=acronym,
            learning_unit_year__academic_year__year=year
        ).select_related(
            'offer_enrollment__student__studentspecificprofile',
            'offer_enrollment__student__person',
            'learning_unit_year__academic_year'
        )
