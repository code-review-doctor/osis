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

from base.ddd.utils.business_validator import TwoStepsMultipleBusinessExceptionListValidator, BusinessValidator
from ddd.logic.application.domain.validator._should_be_an_available_volume import ShouldBeAnAvailableVolume
from ddd.logic.attribution.domain.model.tutor import Tutor
from ddd.logic.attribution.domain.validator._should_distributed_volume_be_a_correct_value import \
    ShouldDistributedVolumeBeACorrectValue
from ddd.logic.attribution.domain.validator._should_tutor_not_be_already_assigned_to_class import \
    ShouldTutorNotBeAlreadyAssignedToClass
from ddd.logic.effective_class_repartition.domain.validator._should_be_numeric_validator import ShouldBeNumericValidator
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity


@attr.s(frozen=True, slots=True)
class DistributeClassToTutorValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    tutor = attr.ib(type=Tutor)
    distributed_volume = attr.ib(type=Decimal)
    effective_class_id = attr.ib(type=EffectiveClassIdentity)
    total_class_volume = attr.ib(type=Decimal)

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return [
            ShouldBeNumericValidator(self.distributed_volume)
        ]

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldDistributedVolumeBeACorrectValue(
                self.total_class_volume,
                self.distributed_volume,
                # FIXME : Need attribution volume !
            ),
            ShouldTutorNotBeAlreadyAssignedToClass(self.effective_class_id, self.tutor),
            ShouldBeAnAvailableVolume(self.distributed_volume, self.total_class_volume),
        ]
