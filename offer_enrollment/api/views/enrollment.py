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
from typing import Optional

from django.conf import settings
from django.db.models import Case, When, Q, F, Value, CharField, Subquery
from django.db.models.functions import Replace, Concat, Lower, Substr
from django.http import Http404
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from backoffice.settings.rest_framework.common_views import LanguageContextSerializerMixin
from base.models.enums import offer_enrollment_state
from base.models.offer_enrollment import OfferEnrollment
from base.models.person import Person
from base.models.student import Student
from education_group.models.enums.cohort_name import CohortName
from offer_enrollment.api.serializers.enrollment import EnrollmentSerializer
from osis_common.ddd.interface import BusinessException

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DoubleNOMAException(BusinessException):
    status_code = "OFFER_ENROLLMENT-1"

    def __init__(self, *args, **kwargs):
        message = _(
            "A problem was detected with your registration : 2 registration id's are linked to your user.</br> Please "
            "contact <a href=\"{registration_department_url}\" "
            "target=\"_blank\">the Registration department</a>. Thank you."
        ).format(registration_department_url=settings.REGISTRATION_ADMINISTRATION_URL)
        super().__init__(message, **kwargs)


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

    @cached_property
    def person(self) -> Person:
        return get_object_or_404(
            Person,
            global_id=self.kwargs['global_id']
        )

    def get_student(self, qs) -> Optional[Student]:
        students = self.person.student_set.all()
        has_to_discriminate = len(students) > 1
        if has_to_discriminate:
            return self.discriminate_student(qs)
        elif students:
            return students.first()
        raise Http404

    @staticmethod
    def discriminate_student(qs) -> Student:
        """
        Discriminate between several student objects that belong to the same person.
        Offer enrollments with valid state enrollment are checked.
        If the most recent enrollment year has only one student, this student is returned.
        If there are more than one student for the most recent offer enrollment year, an exception is raised.
        """
        qs = qs.filter(
            enrollment_state__in=list(offer_enrollment_state.VALID_ENROLLMENT_STATES)
        ).filter(
            education_group_year__academic_year__year=Subquery(
                qs.order_by(
                    '-education_group_year__academic_year__year'
                ).values('education_group_year__academic_year__year')[:1]
            )
        )
        nomas = qs.values('student__registration_id').distinct()
        if len(nomas) > 1:
            raise DoubleNOMAException
        return qs.first().student

    def get_queryset(self):
        qs = self.get_common_queryset().filter(
            student__person__global_id=self.kwargs['global_id']
        )
        student = self.get_student(qs)
        if student:
            qs = qs.filter(student=student)
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
            student_registration_id=F('student__registration_id'),
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
        student = self.get_student(qs)
        if student:
            qs = qs.filter(student=student)
            return self.annotate_queryset(qs)

    @cached_property
    def person(self) -> Person:
        return self.request.user.person
