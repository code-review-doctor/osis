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
from decimal import Decimal
from typing import List

from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db import models
from django.db.models import Q, F, Subquery, OuterRef, Case, When, fields, Sum, Value
from django.db.models.functions import Concat

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from base.models.enums import learning_component_year_type, learning_unit_year_subtypes
from base.models.enums.proposal_type import ProposalType
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit_year import LearningUnitYear
from base.models.proposal_learning_unit import ProposalLearningUnit
from ddd.logic.application.domain.service.i_learning_unit_service import ILearningUnitService
from ddd.logic.application.dtos import LearningUnitVolumeFromServiceDTO, LearningUnitTutorAttributionFromServiceDTO, \
    LearningUnitAnnualVolumeFromServiceDTO, LearningUnitModificationProposalFromServiceDTO
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
        qs = AttributionNew.objects.filter(filter_clause).exclude(
            attributionchargenew__learning_component_year__learning_unit_year__subtype=learning_unit_year_subtypes.PARTIM
        ).annotate(
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

    def search_learning_unit_annual_volume_dto(
            self,
            entity_id: LearningUnitIdentity
    ) -> LearningUnitAnnualVolumeFromServiceDTO:
        qs = LearningComponentYear.objects.filter(
            learning_unit_year__acronym=entity_id.code,
            learning_unit_year__academic_year__year=entity_id.academic_year.year
        ).annotate(
            hourly_volume_total_annual_casted=Case(
                When(hourly_volume_total_annual__isnull=True, then=Decimal(0.0)),
                default=F('hourly_volume_total_annual'),
                output_field=fields.DecimalField()
            )
        ).aggregate(Sum('hourly_volume_total_annual_casted'))['hourly_volume_total_annual_casted__sum']
        return LearningUnitAnnualVolumeFromServiceDTO(volume=qs)

    # TODO: Refactor use learning unit application service instead
    def search_learning_unit_modification_proposal_dto(
            self,
            codes: List[str],
            year: int
    ) -> List[LearningUnitModificationProposalFromServiceDTO]:
        subqs = ProposalLearningUnit.objects.filter(learning_unit_year=OuterRef('pk'))
        qs = LearningUnitYear.objects.filter(
            proposallearningunit__type__in=[
                ProposalType.MODIFICATION.name,
                ProposalType.TRANSFORMATION_AND_MODIFICATION.name
            ]
        ).filter(
            learning_container_year__academic_year__year=year
        ).annotate(
            code=F('learning_container_year__acronym'),
            year=F('learning_container_year__academic_year__year'),
            old_code=Subquery(
                subqs.annotate(code=KeyTextTransform(
                    'acronym',
                    KeyTextTransform('learning_unit_year', 'initial_data'))
                ).values('code')[:1],
                output_field=models.CharField()
            ),
            old_title=Subquery(
                subqs.annotate(
                    common_title=KeyTextTransform(
                        'common_title',
                        KeyTextTransform('learning_container_year', 'initial_data')
                    ),
                    specific_title=KeyTextTransform(
                        'specific_title',
                        KeyTextTransform('learning_unit_year', 'initial_data')
                    )
                ).annotate(
                    title=Case(
                        When(
                            Q(common_title__isnull=True) | Q(common_title__exact='null')
                            | Q(common_title__exact=''),
                            then='specific_title'
                        ),
                        When(
                            Q(specific_title__isnull=True) | Q(specific_title__exact='null') |
                            Q(specific_title__exact=''),
                            then='common_title'
                        ),
                        default=Concat('common_title', Value(' - '), 'specific_title'),
                        output_field=models.CharField(),
                    )
                ).values('title')[:1],
                output_field=models.CharField()
            )
        ).values(
            'code',
            'year',
            'old_code',
            'old_title'
        ).filter(old_code__in=codes)
        return [LearningUnitModificationProposalFromServiceDTO(**row_as_dict) for row_as_dict in qs]
