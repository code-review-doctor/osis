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

import attr

from base.ddd.utils.business_validator import TwoStepsMultipleBusinessExceptionListValidator, BusinessValidator
from ddd.logic.application.domain.validator._should_be_an_available_volume import ShouldBeAnAvailableVolume
from ddd.logic.application.domain.validator._should_be_the_author_of_the_application import \
    ShouldBeTheAuthorOfTheApplication
from ddd.logic.attribution.commands import DistributeClassToTutorCommand
from ddd.logic.effective_class_repartition.domain.validator._should_be_numeric_validator import ShouldBeNumericValidator
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass


@attr.s(frozen=True, slots=True)
class DistributeClassToTutorValidatorList(TwoStepsMultipleBusinessExceptionListValidator):
    command = attr.ib(type=DistributeClassToTutorCommand)
    effective_class = attr.ib(type=EffectiveClass)

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return [
            ShouldBeNumericValidator(self.command.distributed_volume)
        ]

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldBeAnAvailableVolume(self.command, self.effective_class),
        ]
