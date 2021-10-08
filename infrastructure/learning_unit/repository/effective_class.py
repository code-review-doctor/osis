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
from typing import Optional, List, Set

from django.db.models import F, QuerySet, Q, Value
from django.db.models.functions import Concat

from base.models.campus import Campus
from base.models.enums import learning_component_year_type
from base.models.learning_component_year import LearningComponentYear as LearningComponentYearDb
from ddd.logic.learning_unit.builder.effective_class_builder import EffectiveClassBuilder
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass, EffectiveClassIdentity, \
    LecturingEffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.learning_unit.dtos import EffectiveClassFromRepositoryDTO
from ddd.logic.learning_unit.repository.i_effective_class import IEffectiveClassRepository
from learning_unit.models.learning_class_year import LearningClassYear as LearningClassYearDb
from osis_common.ddd.interface import ApplicationService


class EffectiveClassRepository(IEffectiveClassRepository):
    @classmethod
    def get(cls, entity_id: 'EffectiveClassIdentity') -> 'EffectiveClass':
        return EffectiveClassBuilder.build_from_repository_dto(
            cls.get_dto(code=entity_id.complete_class_code, annee=entity_id.learning_unit_identity.year)
        )

    @classmethod
    def search(cls, entity_ids: Optional[List['EffectiveClassIdentity']] = None, **kwargs) -> List['EffectiveClass']:
        if not entity_ids:
            return []
        entity_ids_by_year = itertools.groupby(
            sorted(
                entity_ids,
                key=lambda entity: entity.learning_unit_identity.academic_year.year
            ),
            key=lambda entity: entity.learning_unit_identity.academic_year.year
        )
        dtos = []
        for year, entity_ids_of_same_year in entity_ids_by_year:
            dtos.extend(
                cls.search_dtos(
                    {entity.complete_class_code for entity in entity_ids_of_same_year},
                    year
                )
            )
        builder = EffectiveClassBuilder()
        return [builder.build_from_repository_dto(dto) for dto in dtos]

    @classmethod
    def search_dtos_by_learning_unit(
            cls,
            learning_unit_id: LearningUnitIdentity = None,
            **kwargs
    ) -> List['EffectiveClassFromRepositoryDTO']:
        qs = _get_common_queryset()
        if learning_unit_id:
            qs = qs.filter(
                learning_component_year__learning_unit_year__acronym=learning_unit_id.code,
                learning_component_year__learning_unit_year__academic_year__year=learning_unit_id.year,
            )
        qs = _annotate_queryset(qs)
        qs = _values_queryset(qs)
        return [
            EffectiveClassFromRepositoryDTO(
                class_code=effective_class['class_code'],
                learning_unit_code=effective_class['learning_unit_code'],
                learning_unit_year=effective_class['learning_unit_year'],
                title_fr=effective_class['title_fr'],
                title_en=effective_class['title_en'],
                teaching_place_uuid=effective_class['teaching_place_uuid'],
                derogation_quadrimester=effective_class['derogation_quadrimester'],
                session_derogation=effective_class['session_derogation'],
                volume_q1=effective_class['volume_q1'],
                volume_q2=effective_class['volume_q2'],
                class_type=effective_class['class_type'],
            ) for effective_class in qs
        ]

    @classmethod
    def delete(cls, entity_id: 'EffectiveClassIdentity', **kwargs: ApplicationService) -> None:
        obj = LearningClassYearDb.objects.get(
            acronym=entity_id.class_code,
            learning_component_year__learning_unit_year__academic_year__year=entity_id.learning_unit_identity.year,
            learning_component_year__learning_unit_year__acronym=entity_id.learning_unit_identity.code
        )
        obj.delete()

    @classmethod
    def save(cls, entity: 'EffectiveClass') -> None:
        learning_component_year_id = _get_learning_component_year_id_from_entity(entity)

        campus_id = Campus.objects.filter(
            uuid=entity.teaching_place.uuid,
        ).values_list('pk', flat=True).get()

        LearningClassYearDb.objects.update_or_create(
            learning_component_year_id=learning_component_year_id,
            acronym=entity.entity_id.class_code,
            defaults={
                'title_fr': entity.titles.fr,
                'title_en': entity.titles.en,
                'campus_id': campus_id,
                'quadrimester': entity.derogation_quadrimester.name if entity.derogation_quadrimester else None,
                'session': entity.session_derogation.value if entity.session_derogation else None,
                'hourly_volume_partial_q1': entity.volumes.volume_first_quadrimester,
                'hourly_volume_partial_q2': entity.volumes.volume_second_quadrimester,
            }
        )

    @classmethod
    def get_all_identities(cls) -> List['EffectiveClassIdentity']:  # TODO :: add unit tests
        all_classes = _get_common_queryset().annotate(
            class_code=F('acronym'),
            learning_unit_code=F('learning_component_year__learning_unit_year__acronym'),
            learning_unit_year=F('learning_component_year__learning_unit_year__academic_year__year')
        ).values(
            "class_code",
            "learning_unit_code",
            "learning_unit_year",
        )
        return [
            EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
                class_code=learning_class['class_code'],
                learning_unit_code=learning_class['learning_unit_code'],
                learning_unit_year=learning_class['learning_unit_year'],
            )
            for learning_class in all_classes
        ]

    @classmethod
    def search_dtos(cls, codes: Set[str], annee: int) -> List['EffectiveClassFromRepositoryDTO']:
        codes_sans_tiret = {code.replace('-', '').replace('_', '') for code in codes}
        codes_unites_enseignement = {code[:-1] for code in codes_sans_tiret}
        lettres_classes = {code[-1] for code in codes_sans_tiret}
        qs = _get_common_queryset().filter(
            # Préfiltre sur année pour performances
            learning_component_year__learning_unit_year__academic_year__year=annee,
        ).filter(
            learning_component_year__learning_unit_year__acronym__in=codes_unites_enseignement,
            acronym__in=lettres_classes,
        )
        qs = _annotate_queryset(qs)
        qs = _values_queryset(qs)

        result = list()
        for values in qs:
            if values['class_code'] in lettres_classes and values['learning_unit_code'] in codes_unites_enseignement:
                result.append(EffectiveClassFromRepositoryDTO(**values))
        return result

    @classmethod
    def get_dto(cls, code: str, annee: int) -> 'EffectiveClassFromRepositoryDTO':
        result = cls.search_dtos({code}, annee)
        if result:
            return result[0]


def _get_learning_component_year_id_from_entity(entity: 'EffectiveClass') -> int:
    learning_unit_identity = entity.entity_id.learning_unit_identity
    component_type = learning_component_year_type.LECTURING if isinstance(entity, LecturingEffectiveClass) \
        else learning_component_year_type.PRACTICAL_EXERCISES
    qs = LearningComponentYearDb.objects.select_related(
        'learning_unit_year__academic_year'
    ).filter(
        learning_unit_year__academic_year__year=learning_unit_identity.year,
        learning_unit_year__acronym=learning_unit_identity.code
    )
    if component_type == learning_component_year_type.PRACTICAL_EXERCISES:
        qs = qs.filter(type=component_type)
    else:
        qs = qs.filter(Q(type=component_type) | Q(type__isnull=True, acronym="NT"))

    learning_component_year_id = qs.values_list('pk', flat=True).get()
    return learning_component_year_id


def _annotate_queryset(qs: QuerySet) -> QuerySet:
    return qs.annotate(
        class_code=F('acronym'),
        learning_unit_code=F('learning_component_year__learning_unit_year__acronym'),
        learning_unit_year=F('learning_component_year__learning_unit_year__academic_year__year'),
        teaching_place_uuid=F('campus__uuid'),
        derogation_quadrimester=F('quadrimester'),
        session_derogation=F('session'),
        volume_q1=F('hourly_volume_partial_q1'),
        volume_q2=F('hourly_volume_partial_q2'),
        class_type=F('learning_component_year__type'),
        full_title_fr=Concat(
            'learning_component_year__learning_unit_year__learning_container_year__common_title',
            Value(' - '),
            'title_fr',
        ),
        full_title_en=Concat(
            'learning_component_year__learning_unit_year__learning_container_year__common_title_english',
            Value(' - '),
            'title_en',
        ),
    )


def _values_queryset(qs: QuerySet) -> QuerySet:
    return qs.values(
        'class_code',
        'learning_unit_code',
        'learning_unit_year',
        'title_fr',
        'title_en',
        'teaching_place_uuid',
        'derogation_quadrimester',
        'session_derogation',
        'volume_q1',
        'volume_q2',
        'class_type',
        'full_title_fr',
        'full_title_en',
    )


def _get_common_queryset() -> QuerySet:
    return LearningClassYearDb.objects.all().select_related(
        'learning_component_year',
        'learning_component_year__learning_unit_year',
        'learning_component_year__learning_unit_year__academic_year'
    )
