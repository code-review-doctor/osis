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
from django.db.models import F, Case, When, Q, Value, CharField, Exists, OuterRef
from django.db.models.functions import Concat, Replace
from django.utils.functional import cached_property
from rest_framework import generics
from rest_framework.response import Response

from attribution.api.serializers.attribution import AttributionSerializer
from attribution.calendar.access_schedule_calendar import AccessScheduleCalendar
from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_class import AttributionClass
from base.models.enums import learning_component_year_type, offer_enrollment_state, learning_unit_enrollment_state
from base.models.person import Person
from base.models.student import Student

logger = logging.getLogger(settings.DEFAULT_LOGGER)

COMMON_LEARNING_UNIT_ENROLLMENT_CLAUSE = {
    'offerenrollment__enrollment_state__in': [
        offer_enrollment_state.PROVISORY,
        offer_enrollment_state.SUBSCRIBED
    ],
    'offerenrollment__learningunitenrollment__enrollment_state': learning_unit_enrollment_state.ENROLLED
}


class AttributionListView(generics.ListAPIView):
    """
       Return all attributions of a specific user in a specific year
    """
    name = 'attributions'

    def list(self, request, *args, **kwargs):
        attributions = self._get_attributions_charge_new()
        if self.request.query_params.get('with_effective_class_repartition') == "True":
            # quick fix to be modified with the correct implementation of classes
            attributions = list(attributions) + list(self._get_classes_attributions())
        serializer = AttributionSerializer(
            attributions,
            many=True,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def _get_attributions_charge_new(self):
        return AttributionChargeNew.objects.select_related(
            'attribution',
            'learning_component_year__learning_unit_year__academic_year'
        ).distinct(
            'attribution_id'
        ).filter(
            learning_component_year__learning_unit_year__academic_year__year=self.kwargs['year'],
            attribution__tutor__person=self.person,
            attribution__decision_making=''
        ).annotate(
            # Technical ID for making a match with data in EPC. Remove after refactoring...
            allocation_id=Replace('attribution__external_id', Value('osis.attribution_'), Value('')),

            code=F('learning_component_year__learning_unit_year__acronym'),
            type=F('learning_component_year__learning_unit_year__learning_container_year__container_type'),
            lecturing_charge=Case(
                When(
                    Q(learning_component_year__type=learning_component_year_type.LECTURING),
                    then='allocation_charge',
                ),
                default=None
            ),
            practical_charge=Case(
                When(
                    Q(learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES),
                    then='allocation_charge',
                ),
                default=None
            ),
            title_fr=Case(
                When(
                    Q(learning_component_year__learning_unit_year__learning_container_year__common_title__isnull=True) |
                    Q(learning_component_year__learning_unit_year__learning_container_year__common_title__exact=''),
                    then='learning_component_year__learning_unit_year__specific_title'
                ),
                When(
                    Q(learning_component_year__learning_unit_year__specific_title__isnull=True) |
                    Q(learning_component_year__learning_unit_year__specific_title__exact=''),
                    then='learning_component_year__learning_unit_year__learning_container_year__common_title'
                ),
                default=Concat(
                    'learning_component_year__learning_unit_year__learning_container_year__common_title',
                    Value(' - '),
                    'learning_component_year__learning_unit_year__specific_title'
                ),
                output_field=CharField(),
            ),
            title_en=Case(
                When(
                    Q(learning_component_year__learning_unit_year__learning_container_year__common_title_english__isnull=True) |  # noqa
                    Q(learning_component_year__learning_unit_year__learning_container_year__common_title_english__exact=''),
                    then='learning_component_year__learning_unit_year__specific_title_english'
                ),
                When(
                    Q(learning_component_year__learning_unit_year__specific_title_english__isnull=True) |
                    Q(learning_component_year__learning_unit_year__specific_title_english__exact=''),
                    then='learning_component_year__learning_unit_year__learning_container_year__common_title_english'
                ),
                default=Concat(
                    'learning_component_year__learning_unit_year__learning_container_year__common_title_english',
                    Value(' - '),
                    'learning_component_year__learning_unit_year__specific_title_english'
                ),
                output_field=CharField(),
            ),
            year=F('learning_component_year__learning_unit_year__academic_year__year'),
            credits=F('learning_component_year__learning_unit_year__credits'),
            start_year=F('attribution__start_year'),
            function=F('attribution__function'),
            has_peps=Exists(
                Student.objects.filter(
                    studentspecificprofile__isnull=False,
                    offerenrollment__learningunitenrollment__learning_unit_year__acronym=OuterRef(
                        'learning_component_year__learning_unit_year__acronym'
                    ),
                    offerenrollment__learningunitenrollment__learning_unit_year__academic_year=OuterRef(
                        'learning_component_year__learning_unit_year__academic_year'
                    ),
                    **COMMON_LEARNING_UNIT_ENROLLMENT_CLAUSE
                )
            )
        )

    def _get_classes_attributions(self):
        return AttributionClass.objects.select_related(
            'attribution_charge__attribution',
            'learning_class_year__learning_component_year__learning_unit_year__academic_year'
        ).prefetch_related(

        ).filter(
            learning_class_year__learning_component_year__learning_unit_year__academic_year__year=self.kwargs['year'],
            attribution_charge__attribution__tutor__person=self.person,
            attribution_charge__attribution__decision_making=''  # NEEDED ?
        ).annotate(
            code=F('learning_class_year__learning_component_year__learning_unit_year__acronym'),
            title_fr=Case(
                When(
                    Q(learning_class_year__learning_component_year__learning_unit_year__learning_container_year__common_title__isnull=True) |  # noqa
                    Q(learning_class_year__learning_component_year__learning_unit_year__learning_container_year__common_title__exact=''),
                    then='learning_class_year__title_fr'
                ),
                When(
                    Q(learning_class_year__title_fr__isnull=True) |
                    Q(learning_class_year__title_fr__exact=''),
                    then='learning_class_year__learning_component_year__learning_unit_year__learning_container_year__common_title'
                ),
                default=Concat(
                    'learning_class_year__learning_component_year__learning_unit_year__learning_container_year__common_title',
                    Value(' - '),
                    'learning_class_year__title_fr'
                ),
                output_field=CharField(),
            ),
            title_en=Case(
                When(
                    Q(learning_class_year__learning_component_year__learning_unit_year__learning_container_year__common_title_english__isnull=True) |  # noqa
                    Q(learning_class_year__learning_component_year__learning_unit_year__learning_container_year__common_title_english__exact=''),
                    then='learning_class_year__title_en'
                ),
                When(
                    Q(learning_class_year__title_en__isnull=True) |
                    Q(learning_class_year__title_en__exact=''),
                    then='learning_class_year__learning_component_year__learning_unit_year__learning_container_year__common_title_english'
                ),
                default=Concat(
                    'learning_class_year__learning_component_year__learning_unit_year__learning_container_year__common_title_english',
                    Value(' - '),
                    'learning_class_year__title_en'
                ),
                output_field=CharField(),
            ),
            year=F('learning_class_year__learning_component_year__learning_unit_year__academic_year__year'),
            credits=F('learning_class_year__learning_component_year__learning_unit_year__credits'),
            start_year=F('attribution_charge__attribution__start_year'),
            function=F('attribution_charge__attribution__function'),
            has_peps=Exists(
                Student.objects.filter(
                    studentspecificprofile__isnull=False,
                    offerenrollment__learningunitenrollment__learning_class_year__acronym=OuterRef(
                        'learning_class_year__acronym'
                    ),
                    offerenrollment__learningunitenrollment__learning_class_year__learning_component_year=OuterRef(
                        'learning_class_year__learning_component_year'
                    ),
                    **COMMON_LEARNING_UNIT_ENROLLMENT_CLAUSE
                )
            )
        )

    @cached_property
    def person(self) -> Person:
        return Person.objects.get(global_id=self.kwargs['global_id'])

    def get_serializer_context(self):
        return {
            **super().get_serializer_context(),
            'access_schedule_calendar': AccessScheduleCalendar(),
        }


class MyAttributionListView(AttributionListView):
    """
       Return all attributions of connected user in a specific year
    """
    name = 'my-attributions'

    @cached_property
    def person(self) -> Person:
        return self.request.user.person
