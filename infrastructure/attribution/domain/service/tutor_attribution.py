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
from typing import List

from django.db.models import F, QuerySet, OuterRef, Subquery

from attribution.models.attribution_charge_new import AttributionChargeNew as AttributionChargeNewDb
from attribution.models.attribution_new import AttributionNew as AttributionNewDb
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from ddd.logic.attribution.domain.service.i_tutor_attribution import ITutorAttributionToLearningUnitTranslator
from ddd.logic.attribution.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity


class TutorAttributionToLearningUnitTranslator(ITutorAttributionToLearningUnitTranslator):

    @classmethod
    def search_attributions_to_learning_unit(
            cls,
            learning_unit_identity: 'LearningUnitIdentity',
    ) -> List['TutorAttributionToLearningUnitDTO']:
        qs = _get_common_qs().filter(
            learning_container_year__acronym=learning_unit_identity.code,
            learning_container_year__academic_year__year=learning_unit_identity.year,
        )
        qs = _annotate_qs(qs)
        qs = _value_qs(qs).order_by(
            'last_name',
            'first_name',
        ).distinct()

        return [TutorAttributionToLearningUnitDTO(**data_as_dict) for data_as_dict in qs]

    @classmethod
    def get_learning_unit_attribution(cls, attribution_uuid: str) -> 'TutorAttributionToLearningUnitDTO':
        qs = _get_common_qs().filter(uuid=attribution_uuid)
        qs = _annotate_qs(qs)
        qs = _value_qs(qs)
        tutor_attribution_db = qs.get()
        return TutorAttributionToLearningUnitDTO(**tutor_attribution_db)


def _get_common_qs() -> QuerySet:
    return AttributionNewDb.objects.all()


def _annotate_qs(qs: QuerySet) -> QuerySet:
    lecturing_charge = AttributionChargeNewDb.objects.filter(
        attribution_id=OuterRef('pk'),
        learning_component_year__type=LECTURING
    )
    practical_charge = AttributionChargeNewDb.objects.filter(
        attribution_id=OuterRef('pk'),
        learning_component_year__type=PRACTICAL_EXERCISES
    )
    return qs.annotate(
        learning_unit_code=F('learning_container_year__acronym'),
        learning_unit_year=F('learning_container_year__academic_year__year'),
        attribution_uuid=F('uuid'),
        first_name=F('tutor__person__first_name'),
        last_name=F('tutor__person__last_name'),
        personal_id_number=F('tutor__person__global_id'),
        function=F('function'),
        lecturing_volume_attributed=Subquery(lecturing_charge.values('allocation_charge')[:1]),
        practical_volume_attributed=Subquery(practical_charge.values('allocation_charge')[:1])
    )


def _value_qs(qs: QuerySet) -> QuerySet:
    return qs.values(
        'learning_unit_code',
        'learning_unit_year',
        'attribution_charge_uuid',
        'first_name',
        'last_name',
        'personal_id_number',
        'function',
        'charge_volume_attributed',
    )
