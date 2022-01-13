##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import Optional, List

from django.db import models
from django.db.models import F, QuerySet, Q, Subquery, OuterRef, Case, When, Exists

from attribution.models.attribution_charge_new import AttributionChargeNew
from attribution.models.attribution_new import AttributionNew
from base.auth.roles.tutor import Tutor
from base.models.enums import learning_component_year_type, learning_unit_year_subtypes
from base.models.enums.proposal_type import ProposalType
from base.models.learning_unit_year import LearningUnitYear
from base.models.proposal_learning_unit import ProposalLearningUnit
from ddd.logic.application.domain.builder.applicant_builder import ApplicantBuilder
from ddd.logic.application.domain.model.applicant import ApplicantIdentity, Applicant
from ddd.logic.application.dtos import ApplicantFromRepositoryDTO, AttributionFromRepositoryDTO
from ddd.logic.application.repository.i_applicant_respository import IApplicantRepository


class ApplicantRepository(IApplicantRepository):
    @classmethod
    def search(cls, entity_ids: Optional[List[ApplicantIdentity]] = None, **kwargs) -> List[Applicant]:
        qs = _applicant_base_qs()

        if entity_ids is not None:
            filter_clause = functools.reduce(
                operator.or_,
                ((Q(global_id=entity_id.global_id)) for entity_id in entity_ids)
            )
            qs = qs.filter(filter_clause)

        attributions_qs = _prefetch_attributions(qs, kwargs.get('year'))
        results = []
        for row_as_dict in qs:
            attribution_filtered = [
                attribution for attribution in attributions_qs
                if attribution.applicant_id_global_id == row_as_dict['global_id']
            ]
            dto_from_database = ApplicantFromRepositoryDTO(**row_as_dict, attributions=attribution_filtered)
            results.append(ApplicantBuilder.build_from_repository_dto(dto_from_database))
        return results

    @classmethod
    def get(cls, entity_id: 'ApplicantIdentity') -> 'Applicant':
        qs = _applicant_base_qs().filter(
            global_id=entity_id.global_id
        )
        obj_as_dict = qs.get()
        dto_from_database = ApplicantFromRepositoryDTO(
            **obj_as_dict,
            attributions=_prefetch_attributions(qs)
        )
        return ApplicantBuilder.build_from_repository_dto(dto_from_database)


def _applicant_base_qs() -> QuerySet:
    return Tutor.objects.annotate(
        global_id=F('person__global_id'),
        first_name=F('person__first_name'),
        last_name=F('person__last_name')
    ).values(
        'global_id',
        'first_name',
        'last_name'
    )


def _prefetch_attributions(applicant_qs, year: int = None) -> List[AttributionFromRepositoryDTO]:
    subqs = AttributionChargeNew.objects.filter(attribution__id=OuterRef('id'))

    basic_filter = AttributionNew.objects.filter(
        tutor__person__global_id__in=applicant_qs.values_list('global_id', flat=True), decision_making='')
    if year:
        basic_filter = basic_filter.filter(learning_container_year__academic_year__year=year)

    attributions_as_dict = basic_filter.exclude(
        attributionchargenew__learning_component_year__learning_unit_year__subtype=learning_unit_year_subtypes.PARTIM
    ).annotate(
        course_id_code=F('learning_container_year__acronym'),
        course_id_year=F('learning_container_year__academic_year__year'),
        course_title=Subquery(
            LearningUnitYear.objects.filter(
                learning_container_year_id=OuterRef('learning_container_year_id'),
                subtype=learning_unit_year_subtypes.FULL
            ).annotate_full_title().values('full_title')[:1],
            output_field=models.CharField()
        ),
        course_is_in_suppression_proposal=Exists(
            ProposalLearningUnit.objects.filter(
                learning_unit_year__learning_container_year_id=OuterRef('learning_container_year_id'),
                type=ProposalType.SUPPRESSION.name
            )
        ),
        applicant_id_global_id=F('tutor__person__global_id'),
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
        ),
        is_substitute=Case(
            When(substitute__isnull=False, then=True),
            default=False,
            output_field=models.BooleanField()
        )
    ).values(
        'course_id_code',
        'course_id_year',
        'course_is_in_suppression_proposal',
        'course_title',
        'function',
        'end_year',
        'start_year',
        'applicant_id_global_id',
        'lecturing_volume',
        'practical_volume',
        'is_substitute'
    )
    return [AttributionFromRepositoryDTO(**attribution_as_dict) for attribution_as_dict in attributions_as_dict]
