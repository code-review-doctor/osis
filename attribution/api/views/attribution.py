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
from decimal import Decimal
from typing import Dict, Union, List, Tuple

from django.conf import settings
from django.db.models import F, Case, When, Q, Value, CharField, Exists, OuterRef, Sum, Subquery, BooleanField, \
    DecimalField
from django.db.models.functions import Concat
from django.utils.functional import cached_property
from rest_framework import generics
from rest_framework.response import Response

from attribution.api.serializers.attribution import AttributionSerializer
from attribution.calendar.access_schedule_calendar import AccessScheduleCalendar
from attribution.models.attribution_charge_new import AttributionChargeNew
from base.models.enums import learning_component_year_type, offer_enrollment_state, learning_unit_enrollment_state
from base.models.enums.learning_unit_year_subtypes import PARTIM
from base.models.learning_component_year import LearningComponentYear
from base.models.person import Person
from base.models.student import Student
from ddd.logic.effective_class_repartition.commands import GetTutorRepartitionClassesCommand
from ddd.logic.effective_class_repartition.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.effective_class_repartition.domain.model.tutor import Tutor
from ddd.logic.learning_unit.commands import GetEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from infrastructure.messages_bus import message_bus_instance
from learning_unit.models.learning_class_year import LearningClassYear

logger = logging.getLogger(settings.DEFAULT_LOGGER)

EffectiveClassRepartitionDict = Dict[str, Union[str, bool]]
ClassPepsTuple = Tuple[str, bool]

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
        if self.request.query_params.get('with_effective_class_repartition') == "True" and self.attributions_charge_new:
            # quick fix to be modified with the correct implementation of classes
            self._fill_classes_repartition()
        serializer = AttributionSerializer(
            self.attributions_charge_new,
            many=True,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @cached_property
    def attributions_charge_new(self):
        attributions = AttributionChargeNew.objects.select_related(
            'attribution',
            'learning_component_year__learning_unit_year__academic_year'
        ).filter(
            learning_component_year__learning_unit_year__academic_year__year=self.kwargs['year'],
            attribution__tutor__person=self.person,
            attribution__decision_making=''
        ).distinct(
            'attribution_id'
        ).annotate(
            tutor_personal_id=F('attribution__tutor__person__global_id'),

            code=F('learning_component_year__learning_unit_year__acronym'),
            type=F('learning_component_year__learning_unit_year__learning_container_year__container_type'),
            lecturing_charge=Case(
                When(
                    Q(learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES),
                    then=Subquery(
                        AttributionChargeNew.objects.filter(
                            attribution_id=OuterRef('attribution_id'),
                            learning_component_year__type=learning_component_year_type.LECTURING
                        ).values('allocation_charge')[:1]
                    ),
                ),
                default=F('allocation_charge')
            ),
            practical_charge=Case(
                When(
                    Q(learning_component_year__type=learning_component_year_type.LECTURING) |
                    Q(learning_component_year__acronym='NT'),
                    then=Subquery(
                        AttributionChargeNew.objects.filter(
                            attribution_id=OuterRef('attribution_id'),
                            learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES
                        ).values('allocation_charge')[:1]
                    ),
                ),
                default=F('allocation_charge')
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
                    Q(learning_component_year__learning_unit_year__learning_container_year__common_title_english__exact=''),  # noqa
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
                    offerenrollment__learningunitenrollment__learning_unit_year_id=OuterRef(
                        'learning_component_year__learning_unit_year_id'
                    ),
                    **COMMON_LEARNING_UNIT_ENROLLMENT_CLAUSE
                )
            ),
            is_partim=Case(
                When(
                    Q(learning_component_year__learning_unit_year__subtype=PARTIM),
                    then=True,
                ),
                default=False,
                output_field=BooleanField()
            ),
            total_learning_unit_charge=Subquery(
                LearningComponentYear.objects.filter(
                    learning_unit_year_id=OuterRef('learning_component_year__learning_unit_year_id')
                ).values(
                    'learning_unit_year_id'
                ).annotate(
                    volume_global=Sum(
                        (F('hourly_volume_total_annual') or Decimal(0)) * (F('planned_classes') or Decimal(0)),
                        output_field=DecimalField()
                    ),

                ).values('volume_global')[:1],
            ),
        )
        return attributions

    def _fill_classes_repartition(self):
        tutor_classes = message_bus_instance.invoke(
            GetTutorRepartitionClassesCommand(
                tutor_personal_id_number=self.attributions_charge_new[0].tutor_personal_id
            )
        )  # type: Tutor
        classes_peps = self._get_classes_peps(tutor_classes, year=self.kwargs['year'])
        for attrib in self.attributions_charge_new:
            if tutor_classes:
                learning_unit_year = attrib.learning_component_year.learning_unit_year
                classes_repartition = tutor_classes.get_classes_repartition_on_learning_unit(
                    learning_unit_code=learning_unit_year.acronym,
                    learning_unit_year=learning_unit_year.academic_year.year
                )
                attrib.effective_class_repartition = self._get_classes_repartition(classes_repartition, classes_peps)
            else:
                attrib.effective_class_repartition = []

    @staticmethod
    def _get_classes_peps(tutor_classes: 'Tutor', year: int) -> List[ClassPepsTuple]:
        class_codes = [
            "{}{}".format(
                class_repartition.effective_class.learning_unit_identity.code,
                class_repartition.effective_class.class_code
            ) for class_repartition in tutor_classes.distributed_effective_classes
        ] if tutor_classes else []
        classes_peps = LearningClassYear.objects.annotate(
            full_code=Concat('learning_component_year__learning_unit_year__acronym', 'acronym')
        ).filter(
            full_code__in=class_codes,
        ).annotate(
            has_peps=Exists(
                Student.objects.filter(
                    studentspecificprofile__isnull=False,
                    offerenrollment__learningunitenrollment__learning_class_year__acronym=OuterRef('acronym'),
                    offerenrollment__learningunitenrollment__learning_unit_year_id=OuterRef(
                        'learning_component_year__learning_unit_year_id'
                    ),
                    **COMMON_LEARNING_UNIT_ENROLLMENT_CLAUSE
                )
            )
        ).values_list(
            'full_code', 'has_peps'
        )
        return list(classes_peps)

    @staticmethod
    def _get_classes_repartition(
            classes_repartition: List[ClassVolumeRepartition],
            classes_peps: List[ClassPepsTuple]
    ) -> List[EffectiveClassRepartitionDict]:
        effective_class_repartition = []
        for class_repartition in classes_repartition:
            effective_class = message_bus_instance.invoke(
                GetEffectiveClassCommand(
                    class_code=class_repartition.class_code,
                    learning_unit_year=class_repartition.effective_class.learning_unit_identity.year,
                    learning_unit_code=class_repartition.effective_class.learning_unit_identity.code
                )
            )  # type: EffectiveClass
            clean_code = effective_class.complete_acronym.replace('_', '').replace('-', '')
            effective_class_repartition.append(
                {
                    'code': effective_class.complete_acronym,
                    'title_fr': effective_class.titles.fr,
                    'title_en': effective_class.titles.en,
                    'has_peps': next(peps for code, peps in classes_peps if code == clean_code)
                }
            )
        return effective_class_repartition

    @cached_property
    def person(self) -> Person:
        return Person.objects.get(global_id=self.kwargs['global_id'])

    def get_serializer_context(self):
        return {
            **super().get_serializer_context(),
            'access_schedule_calendar': AccessScheduleCalendar(),
            'year': self.kwargs['year'],
        }


class MyAttributionListView(AttributionListView):
    """
       Return all attributions of connected user in a specific year
    """
    name = 'my-attributions'

    @cached_property
    def person(self) -> Person:
        return self.request.user.person
