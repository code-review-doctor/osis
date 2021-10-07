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
from typing import Optional, List, Set

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from base.models.enums.learning_component_year_type import LECTURING
from base.models.enums.learning_component_year_type import PRACTICAL_EXERCISES
from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.builder.effective_class_builder import EffectiveClassBuilder
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.domain.model._financial_volumes_repartition import DurationUnit
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass, EffectiveClassIdentity
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.learning_unit.dtos import EffectiveClassFromRepositoryDTO
from ddd.logic.learning_unit.repository.i_effective_class import IEffectiveClassRepository


class EffectiveClassRepository(InMemoryGenericRepository, IEffectiveClassRepository):
    entities = list()  # type: List[EffectiveClass]
    dtos = [
        EffectiveClassFromRepositoryDTO(
            class_code='A',
            learning_unit_code='LDROI1001',
            learning_unit_year=2020,
            title_fr='Intitulé spécifique à la classe effective',
            title_en='Specific title of the effective class',
            teaching_place_uuid='teaching-place-uuid',
            derogation_quadrimester=DerogationQuadrimester.Q1.name,
            session_derogation=DerogationSession.DEROGATION_SESSION_1XX.value,
            volume_q1=DurationUnit(5.0),
            volume_q2=DurationUnit(0.0),  # FIXME :: peut avoir une valeur à 0.0 ?
            class_type=LECTURING,
        ),
        EffectiveClassFromRepositoryDTO(
            class_code='X',
            learning_unit_code='LDROI1001',
            learning_unit_year=2021,
            title_fr='Intitulé spécifique à la classe effective',
            title_en='Specific title of the effective class',
            teaching_place_uuid='teaching-place-uuid',
            derogation_quadrimester=DerogationQuadrimester.Q1.name,
            session_derogation=DerogationSession.DEROGATION_SESSION_1XX.value,
            volume_q1=DurationUnit(5.0),
            volume_q2=DurationUnit(0.0),  # FIXME :: peut avoir une valeur à 0.0 ?
            class_type=LECTURING,
        ),
    ]

    @classmethod
    def search(cls, entity_ids: Optional[List['EffectiveClassIdentity']] = None, **kwargs) -> List['EffectiveClass']:
        builder = EffectiveClassBuilder()
        identity_builder = EffectiveClassIdentityBuilder()
        return [
            builder.build_from_repository_dto(dto)
            for dto in cls.dtos
            if identity_builder.build_from_repository_dto(dto) in entity_ids
        ]

    @classmethod
    def search_dtos(cls, codes: Set[str], annee: int) -> List['EffectiveClassFromRepositoryDTO']:
        return [
            dto for dto in cls.dtos if dto.code_complet_classe in codes and dto.learning_unit_year == annee
        ]

    @classmethod
    def get_dto(cls, code: str, annee: int) -> 'EffectiveClassFromRepositoryDTO':
        dtos = cls.search_dtos({code}, annee)
        if dtos:
            return dtos[0]

    @classmethod
    def search_dtos_by_learning_unit(
            cls,
            learning_unit_id: Optional['LearningUnitIdentity'] = None,
            **kwargs
    ) -> List['EffectiveClassFromRepositoryDTO']:
        class_to_return = []
        for effective_class in cls.entities:
            if effective_class.learning_unit_identity == learning_unit_id:
                dto = EffectiveClassFromRepositoryDTO(
                    class_code=effective_class.class_code,
                    learning_unit_code=effective_class.learning_unit_code,
                    learning_unit_year=effective_class.year,
                    title_fr=effective_class.titles.fr,
                    title_en=effective_class.titles.en,
                    teaching_place_uuid=effective_class.teaching_place.uuid,
                    derogation_quadrimester=effective_class.derogation_quadrimester,
                    session_derogation=effective_class.session_derogation,
                    volume_q1=effective_class.volumes.volume_first_quadrimester,
                    volume_q2=effective_class.volumes.volume_second_quadrimester,
                    class_type=LECTURING if effective_class.is_lecturing else PRACTICAL_EXERCISES,
                )
                class_to_return.append(dto)
        return class_to_return
