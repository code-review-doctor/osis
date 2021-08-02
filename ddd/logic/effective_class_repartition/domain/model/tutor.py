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
from decimal import Decimal
from typing import List

import attr

from ddd.logic.effective_class_repartition.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.effective_class_repartition.domain.model._learning_unit_attribution import \
    LearningUnitAttributionIdentity
from ddd.logic.effective_class_repartition.domain.validator.validators_by_business_action import \
    DistributeClassToTutorValidatorList
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class TutorIdentity(interface.EntityIdentity):
    personal_id_number = attr.ib(type=str)


# TODO :: rename context to effective_class_distribution

@attr.s(slots=True, hash=False, eq=False)
class Tutor(interface.RootEntity):
    entity_id = attr.ib(type=TutorIdentity)
    distributed_effective_classes = attr.ib(type=List[ClassVolumeRepartition])

    def assign_class(
            self,
            effective_class_id: 'EffectiveClassIdentity',
            learning_unit_attribution_uuid: str,
            distributed_volume: Decimal,
    ) -> None:
        DistributeClassToTutorValidatorList(self, effective_class_id).validate()
        class_volume = ClassVolumeRepartition(
            effective_class=effective_class_id,
            distributed_volume=distributed_volume,
            attribution=LearningUnitAttributionIdentity(uuid=learning_unit_attribution_uuid),
        )
        self.distributed_effective_classes.append(class_volume)

    def edit_distributed_volume(
            self,
            class_code: str,
            learning_unit_attribution_uuid: str,
            distributed_volume: Decimal,
    ) -> None:
        for class_volume in self.distributed_effective_classes:
            attribution_uuid = class_volume.attribution.uuid
            effective_class_code = class_volume.effective_class.class_code
            if attribution_uuid == learning_unit_attribution_uuid and class_code == effective_class_code:
                class_volume.distributed_volume = distributed_volume

    def unassign_class(self, class_code: str, learning_unit_attribution_uuid: str) -> None:
        for class_volume in self.distributed_effective_classes:
            attribution_uuid = class_volume.attribution.uuid
            effective_class_code = class_volume.effective_class.class_code
            if attribution_uuid == learning_unit_attribution_uuid and class_code == effective_class_code:
                self.distributed_effective_classes.remove(class_volume)
