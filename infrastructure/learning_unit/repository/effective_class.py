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
from typing import Optional, List

from django.db.models import F, QuerySet

from base.models.campus import Campus
from base.models.enums import learning_component_year_type
from base.models.learning_component_year import LearningComponentYear as LearningComponentYearDb
from ddd.logic.learning_unit.builder.effective_class_builder import EffectiveClassBuilder
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass, EffectiveClassIdentity, \
    LecturingEffectiveClass
from ddd.logic.learning_unit.dtos import EffectiveClassFromRepositoryDTO
from ddd.logic.learning_unit.repository.i_effective_class import IEffectiveClassRepository
from learning_unit.models.learning_class_year import LearningClassYear as LearningClassYearDb
from osis_common.ddd.interface import ApplicationService


class EffectiveClassRepository(IEffectiveClassRepository):
    @classmethod
    def get(cls, entity_id: 'EffectiveClassIdentity') -> 'EffectiveClass':
        learning_unit_id = entity_id.learning_unit_identity
        qs = LearningClassYearDb.objects.filter(
            learning_component_year__learning_unit_year__acronym=learning_unit_id.code,
            learning_component_year__learning_unit_year__academic_year__year=learning_unit_id.year,
            acronym=entity_id.code,
        )
        qs = _annotate_queryset(qs)
        qs = _values_queryset(qs)
        obj_as_dict = qs.get()
        dto_from_database = EffectiveClassFromRepositoryDTO(**obj_as_dict)
        return EffectiveClassBuilder.build_from_repository_dto(dto_from_database)

    @classmethod
    def search(cls, entity_ids: Optional[List['EffectiveClassIdentity']] = None, **kwargs) -> List['EffectiveClass']:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: 'EffectiveClassIdentity', **kwargs: ApplicationService) -> None:
        raise NotImplementedError

    @classmethod
    def save(cls, entity: 'EffectiveClass') -> None:
        learning_component_year_id = _get_learning_component_year_id_from_entity(entity)

        campus_id = Campus.objects.filter(
            name=entity.teaching_place.place,
            organization__name=entity.teaching_place.organization_name
        ).values_list('pk', flat=True).get()

        LearningClassYearDb.objects.create(
            learning_component_year_id=learning_component_year_id,
            acronym=entity.entity_id.code,
            title_fr=entity.titles.fr,
            title_en=entity.titles.en,
            campus_id=campus_id,
            quadrimester=entity.derogation_quadrimester.name,
            session=entity.session_derogation,
            hourly_volume_partial_q1=entity.volumes.volume_first_quadrimester,
            hourly_volume_partial_q2=entity.volumes.volume_second_quadrimester,
            hourly_volume_total_annual=entity.volumes.volume_annual
        )


def _get_learning_component_year_id_from_entity(entity: 'EffectiveClass') -> int:
    learning_unit_identity = entity.entity_id.learning_unit_identity
    component_type = learning_component_year_type.LECTURING if isinstance(entity, LecturingEffectiveClass) \
        else learning_component_year_type.PRACTICAL_EXERCISES
    learning_component_year_id = LearningComponentYearDb.objects.filter(
        type=component_type,
        learning_unit_year__academic_year__year=learning_unit_identity.year,
        learning_unit_year__acronym=learning_unit_identity.code
    ).values_list('pk', flat=True).get()
    return learning_component_year_id


def _annotate_queryset(qs: QuerySet) -> QuerySet:
    return qs.annotate(
        class_code=F('acronym'),
        learning_unit_code=F('learning_component_year__learning_unit_year__acronym'),
        learning_unit_year=F('learning_component_year__learning_unit_year__academic_year__year'),
        teaching_place=F('campus__name'),
        teaching_organization=F('campus__organization__name'),
        derogation_quadrimester=F('quadrimester'),
        session_derogation=F('session'),
        volume_q1=F('hourly_volume_partial_q1'),
        volume_q2=F('hourly_volume_partial_q2'),
        volume_annual=F('hourly_volume_total_annual'),
        class_type=F('learning_component_year__type')
    )


def _values_queryset(qs: QuerySet) -> QuerySet:
    return qs.values(
        'class_code',
        'learning_unit_code',
        'learning_unit_year',
        'title_fr',
        'title_en',
        'teaching_place',
        'teaching_organization',
        'derogation_quadrimester',
        'session_derogation',
        'volume_q1',
        'volume_q2',
        'volume_annual',
        'class_type'
    )
