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
from typing import Union

from ddd.logic.effective_class_repartition.builder.tutor_identity_builder import TutorIdentityBuilder
from ddd.logic.effective_class_repartition.commands import DistributeClassToTutorCommand, \
    EditClassVolumeRepartitionToTutorCommand
from ddd.logic.effective_class_repartition.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.effective_class_repartition.domain.model._learning_unit_attribution import \
    LearningUnitAttributionIdentity
from ddd.logic.effective_class_repartition.domain.model.tutor import Tutor
from ddd.logic.effective_class_repartition.dtos import TutorSearchDTO, \
    DistributedEffectiveClassesDTO
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from osis_common.ddd import interface


class TutorBuilder(interface.RootEntityBuilder):

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'TutorSearchDTO') -> 'Tutor':
        tutor_identity = TutorIdentityBuilder.build_from_personal_id_number(
            personal_id_number=dto_object.personal_id_number
        )
        return Tutor(
            entity_id=tutor_identity,
            distributed_effective_classes=[
                _build_repartition(dto) for dto in dto_object.distributed_classes
            ]
        )

    @classmethod
    def build_from_command(
            cls,
            cmd: Union['DistributeClassToTutorCommand', 'EditClassVolumeRepartitionToTutorCommand']
    ) -> 'Tutor':
        tutor_identity = TutorIdentityBuilder.build_from_personal_id_number(
            personal_id_number=cmd.tutor_personal_id_number
        )
        return Tutor(
            entity_id=tutor_identity,
            distributed_effective_classes=[],
        )


def _build_repartition(dto: 'DistributedEffectiveClassesDTO') -> ClassVolumeRepartition:
    return ClassVolumeRepartition(
        effective_class=EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
            class_code=dto.class_code,
            learning_unit_code=dto.learning_unit_code,
            learning_unit_year=dto.learning_unit_year
        ),
        distributed_volume=dto.distributed_volume,
        attribution=LearningUnitAttributionIdentity(uuid=dto.attribution_uuid),
    )
