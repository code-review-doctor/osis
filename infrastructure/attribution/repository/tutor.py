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
import itertools
from typing import List, Optional

from django.db.models import F, QuerySet, Q

from attribution.models.attribution_charge_new import AttributionChargeNew as AttributionChargeNewDatabase
from attribution.models.attribution_class import AttributionClass as AttributionClassDatabase
from attribution.models.attribution_new import AttributionNew as AttributionNewDatabase
from ddd.logic.attribution.builder.tutor_builder import TutorBuilder
from ddd.logic.attribution.domain.model.tutor import Tutor, TutorIdentity
from ddd.logic.attribution.dtos import TutorSearchDTO, \
    DistributedEffectiveClassesDTO
from ddd.logic.attribution.repository.i_tutor import ITutorRepository
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from learning_unit.models.learning_class_year import LearningClassYear as LearningClassYearDatabase
from osis_common.ddd.interface import ApplicationService


class TutorRepository(ITutorRepository):

    @classmethod
    def delete(cls, entity_id: 'TutorIdentity', **kwargs: ApplicationService) -> None:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'TutorIdentity') -> 'Tutor':
        tutors = cls.search(entity_ids=[entity_id])
        if tutors:
            return tutors[0]

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['TutorIdentity']] = None,
            learning_unit_identity: 'LearningUnitIdentity' = None,
            effective_class_identity: 'EffectiveClassIdentity' = None,
    ) -> List['Tutor']:

        qs = _get_common_queryset()

        if learning_unit_identity:
            code = learning_unit_identity.code
            year = learning_unit_identity.year
            qs = qs.filter(
                attribution_charge__learning_component_year__learning_unit_year__acronym=code,
                attribution_charge__learning_component_year__learning_unit_year__academic_year__year=year,
            )

        if effective_class_identity:
            learning_unit_code = effective_class_identity.learning_unit_identity.code
            year = effective_class_identity.learning_unit_identity.year
            qs = qs.filter(
                learning_class_year__acronym=effective_class_identity.class_code,
                learning_class_year__learning_component_year__learning_unit_year__acronym=learning_unit_code,
                learning_class_year__learning_component_year__learning_unit_year__academic_year__year=year,
            )

        if entity_ids:
            distinct_ids = {e.personal_id_number for e in entity_ids}
            qs = qs.filter(attribution_charge__attribution__tutor__person__global_id__in=distinct_ids)

        qs = _annotate_queryset(qs)
        qs = _values_qs(qs)

        result = []

        classes_grouped_by_tutor = itertools.groupby(qs.values(), lambda obj: obj['personal_id_number'])
        for personal_id_number, distributed_classes_as_dict in classes_grouped_by_tutor:
            distributed_classes = [
                DistributedEffectiveClassesDTO(
                    class_code=distributed_class['class_code'],
                    learning_unit_code=distributed_class['learning_unit_code'],
                    learning_unit_year=distributed_class['learning_unit_year'],
                    distributed_volume=distributed_class['volume'],
                    attribution_uuid=distributed_class['attribution_uuid'],
                )
                for distributed_class in distributed_classes_as_dict
            ]
            tutor = TutorBuilder.build_from_repository_dto(
                TutorSearchDTO(
                    personal_id_number=personal_id_number,
                    distributed_classes=distributed_classes
                )
            )
            result.append(tutor)
        return result

    @classmethod
    def save(cls, entity: 'Tutor') -> None:
        for distributed_class in entity.distributed_effective_classes:
            effective_class_identity = distributed_class.effective_class
            learning_unit_identity = effective_class_identity.learning_unit_identity
            learning_class_year = LearningClassYearDatabase.objects.get(
                learning_component_year__learning_unit_year__acronym=learning_unit_identity.code,
                learning_component_year__learning_unit_year__academic_year__year=learning_unit_identity.year,
                acronym=effective_class_identity.class_code
            )

            attribution_charge_id = AttributionChargeNewDatabase.objects.filter(
                attribution__uuid=distributed_class.attribution.uuid,
                learning_component_year_id=learning_class_year.learning_component_year_id,
            ).values_list('pk', flat=True).get()

            attribution_class, _ = AttributionClassDatabase.objects.update_or_create(
                attribution_charge_id=attribution_charge_id,
                learning_class_year=learning_class_year,
                defaults={
                    'allocation_charge': distributed_class.distributed_volume
                }
            )

        persisted_tutor = cls.get(entity_id=entity.entity_id)
        if persisted_tutor:
            to_remove = set(persisted_tutor.distributed_effective_classes) - set(entity.distributed_effective_classes)
            for distributed_class in to_remove:
                _get_common_queryset().filter(
                    attribution_charge__attribution__uuid=distributed_class.attribution.uuid,
                    learning_class_year__acronym=distributed_class.effective_class.class_code,
                ).delete()


def _get_common_queryset() -> QuerySet:
    return AttributionClassDatabase.objects.all()


def _annotate_queryset(qs: QuerySet) -> QuerySet:
    return qs.annotate(
        personal_id_number=F('attribution_charge__attribution__tutor__person__global_id'),
        attribution_uuid=F('attribution_charge__attribution__uuid'),
        volume=F('allocation_charge'),
        learning_unit_code=F('attribution_charge__learning_component_year__learning_unit_year__acronym'),
        learning_unit_year=F('attribution_charge__learning_component_year__learning_unit_year__academic_year__year'),
        class_code=F('learning_class_year__acronym'),
    )


def _values_qs(qs: QuerySet) -> QuerySet:
    return qs.values(
        "personal_id_number",
        "attribution_uuid",
        "volume",
        'learning_unit_code',
        'learning_unit_year',
        'class_code',
    )
