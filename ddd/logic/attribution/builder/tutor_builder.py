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

from ddd.logic.attribution.builder.tutor_identity_builder import TutorIdentityBuilder
from ddd.logic.attribution.domain.model._attribution import LearningUnitAttribution, LearningUnitAttributionIdentity
from ddd.logic.attribution.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.attribution.domain.model.tutor import Tutor
from ddd.logic.attribution.dtos import LearningUnitAttributionFromRepositoryDTO, TutorSearchDTO, \
    DistributedEffectiveClassesDTO
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from osis_common.ddd import interface


class TutorBuilder(interface.RootEntityBuilder):

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'TutorSearchDTO') -> 'Tutor':
        tutor_identity = TutorIdentityBuilder.build_from_personal_id_number(
            personal_id_number=dto_object.personal_id_number
        )
        return Tutor(
            entity_id=tutor_identity,
            last_name=dto_object.last_name,
            first_name=dto_object.first_name,
            attributions=[build_attribution(attribution) for attribution in dto_object.attributions]
        )


def build_attribution(attribution: 'LearningUnitAttributionFromRepositoryDTO') -> 'LearningUnitAttribution':
    return LearningUnitAttribution(
        entity_id=LearningUnitAttributionIdentity(uuid=attribution.attribution_uuid),
        function=attribution.function,
        learning_unit=LearningUnitIdentityBuilder.build_from_code_and_year(
            attribution.learning_unit_code,
            attribution.learning_unit_year
        ),
        distributed_effective_classes=_get_distributed_effective_classes(
            attribution.attribution_volume,
            attribution.effective_classes
        )
    )


def _get_distributed_effective_classes(
        volume: float,
        effective_classes: List['DistributedEffectiveClassesDTO']
) -> List[ClassVolumeRepartition]:
    return [
        ClassVolumeRepartition(
            effective_class=EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
                class_code=effective_classe.class_code,
                learning_unit_code=effective_classe.learning_unit_code,
                learning_unit_year=effective_classe.learning_unit_year
            ),
            distributed_volume=volume
        ) for effective_classe in effective_classes
    ]
