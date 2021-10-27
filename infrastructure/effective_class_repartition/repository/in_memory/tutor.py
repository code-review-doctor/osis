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
import datetime
from decimal import Decimal
from typing import List, Optional, Union

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.effective_class_repartition.domain.model.tutor import Tutor, TutorIdentity
from ddd.logic.effective_class_repartition.dtos import TutorSearchDTO, DistributedEffectiveClassesDTO
from ddd.logic.effective_class_repartition.repository.i_tutor import ITutorRepository
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity


class TutorRepository(InMemoryGenericRepository, ITutorRepository):
    entities = list()  # type: List[Tutor]

    tutor_dtos = [
        TutorSearchDTO(
            personal_id_number='00321234',
            distributed_classes=[
                DistributedEffectiveClassesDTO(
                    class_code='X',
                    learning_unit_code='LDROI1001',
                    code_complet_classe='LDROI1001-X',
                    learning_unit_year=datetime.date.today().year,
                    distributed_volume=Decimal(5.0),
                    attribution_uuid='attribution_uuid1',
                ),
            ]
        )
    ]

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List['TutorIdentity']] = None,
            effective_class_identity: 'EffectiveClassIdentity' = None,
    ) -> List['Tutor']:
        # TODO :: should reuse cls.search_dto()
        return list(
            filter(
                lambda tutor: _filter(tutor, entity_ids, effective_class_identity),
                cls.entities
            )
        )

    @classmethod
    def search_dto(
            cls,
            entity_ids: Optional[List['TutorIdentity']] = None,
            effective_class_identity: 'EffectiveClassIdentity' = None,
    ) -> List['TutorSearchDTO']:
        return list(
            filter(
                lambda tutor_dto: _filter_condition_dto(tutor_dto, entity_ids, effective_class_identity),
                cls.tutor_dtos
            )
        )


def _filter(
        tutor: 'Tutor',
        entity_ids: Optional[List['TutorIdentity']],
        effective_class_identity: 'EffectiveClassIdentity'
):
    class_identities = [class_repartition.effective_class for class_repartition in tutor.distributed_effective_classes]
    if effective_class_identity and effective_class_identity in class_identities:
        return True
    if entity_ids and tutor.entity_id in entity_ids:
        return True
    return False


def _filter_condition_dto(
        tutor_dto: 'TutorSearchDTO',
        entity_ids: Optional[List['TutorIdentity']],
        effective_class_identity: 'EffectiveClassIdentity',
):
    class_identities = [
        EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
            class_repartition.class_code,
            class_repartition.learning_unit_code,
            class_repartition.learning_unit_year,
        ) for class_repartition in tutor_dto.distributed_classes
    ]
    if effective_class_identity and effective_class_identity in class_identities:
        return True
    tutor_entity_id = TutorIdentity(personal_id_number=tutor_dto.personal_id_number)
    if entity_ids and tutor_entity_id in entity_ids:
        return True
    return False
