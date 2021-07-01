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
import functools
import operator
from typing import List

from django.db import models
from django.db.models import Q, F, Subquery, OuterRef

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from base.models.enums import learning_component_year_type
from base.models.learning_unit_year import LearningUnitYear
from ddd.logic.application.domain.service.i_learning_unit_service import ILearningUnitService
from ddd.logic.application.dtos import LearningUnitVolumeFromServiceDTO, LearningUnitTutorAttributionFromServiceDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity


class LearningUnitTranslator(ILearningUnitService):
    # TODO: Refactor use learning unit application service instead
    def search_learning_unit_volumes_dto(
            self, entity_ids: List[LearningUnitIdentity]
    ) -> List[LearningUnitVolumeFromServiceDTO]:
        filter_clause = functools.reduce(
            operator.or_,
            (
                (Q(acronym=entity_id.code) & Q(academic_year__year=entity_id.academic_year.year))
                for entity_id in entity_ids
            )
        )

        qs = LearningUnitYear.objects.filter(filter_clause).\
            annotate_volume_total().\
            annotate(
                code=F('acronym'),
                year=F('academic_year__year')
            ).\
            values(
                'code',
                'year',
                'lecturing_volume_total',
                'practical_volume_total',
            )
        return [LearningUnitVolumeFromServiceDTO(**row_as_dict) for row_as_dict in qs]

    # TODO: Refactor use learning unit application service instead
    def search_tutor_attribution_dto(
            self,
            entity_ids: List[LearningUnitIdentity]
    ) -> List[LearningUnitTutorAttributionFromServiceDTO]:
        filter_clause = functools.reduce(
            operator.or_,
            (
                (Q(learning_container_year__acronym=entity_id.code)
                 & Q(learning_container_year__academic_year__year=entity_id.academic_year.year)
                 ) for entity_id in entity_ids)
        )
        subqs = AttributionChargeNew.objects.filter(attribution__id=OuterRef('id'))
        qs = AttributionNew.objects.filter(filter_clause).annotate(
            code=F('learning_container_year__acronym'),
            year=F('learning_container_year__academic_year__year'),
            first_name=F('tutor__person__first_name'),
            last_name=F('tutor__person__last_name'),
            lecturing_volume=Subquery(
                subqs.filter(
                    learning_component_year__type=learning_component_year_type.LECTURING
                ).values('allocation_charge')[:1],
                output_field=models.DecimalField()
            ),
            practical_volume=Subquery(
                subqs.filter(
                    learning_component_year__type=learning_component_year_type.PRACTICAL_EXERCISES
                ).values('allocation_charge')[:1],
                output_field=models.DecimalField()
            )
        ).values(
            'code',
            'year',
            'first_name',
            'last_name',
            'function',
            'lecturing_volume',
            'practical_volume',
        )
        return [LearningUnitTutorAttributionFromServiceDTO(**row_as_dict) for row_as_dict in qs]
