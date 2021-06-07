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

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.learning_unit.builder.effective_class_builder import EffectiveClassBuilder
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from ddd.logic.learning_unit.domain.service.can_access_creation_effective_class import CanAccessCreationEffectiveClass
from ddd.logic.learning_unit.domain.validator.exceptions import CodeClassAlreadyExistForUeException, \
    AnnualVolumeInvalidException
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository
from osis_common.ddd import interface


class CreateEffectiveClass(interface.DomainService):

    @classmethod
    def create(
            cls,
            learning_unit: 'LearningUnit',
            cmd: 'CreateEffectiveClassCommand',
            all_existing_class_identities: List['EffectiveClassIdentity'],
            learning_unit_repository: 'ILearningUnitRepository'
    ):
        CanAccessCreationEffectiveClass().check(
            learning_unit=learning_unit,
            learning_unit_repository=learning_unit_repository
        )

        exceptions = set()  # type Set[BusinessException]

        if _is_effective_class_volumes_inconsistent_with_learning_unit_volume_annual(learning_unit, cmd):
            exceptions.add(AnnualVolumeInvalidException(learning_unit))

        if all_existing_class_identities:
            for class_id in all_existing_class_identities:
                if class_id.learning_unit_identity == learning_unit.entity_id and class_id.class_code == cmd.class_code:
                    exceptions.add(CodeClassAlreadyExistForUeException(learning_unit.entity_id, cmd.class_code))

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)

        effective_class = EffectiveClassBuilder.build_from_command(
            cmd=cmd,
            learning_unit=learning_unit
        )
        return effective_class


def _is_effective_class_volumes_inconsistent_with_learning_unit_volume_annual(
        learning_unit: 'LearningUnit',
        cmd: 'CreateEffectiveClassCommand'
) -> Decimal:
    practical_part = learning_unit.practical_part
    lecturing_part = learning_unit.lecturing_part

    if practical_part and not lecturing_part:
        volume_annual = practical_part.volumes.volume_annual
    else:
        volume_annual = lecturing_part.volumes.volume_annual
    if (cmd.volume_first_quadrimester is None or cmd.volume_first_quadrimester == 0) and \
            (cmd.volume_second_quadrimester is None or cmd.volume_second_quadrimester == 0):
        return False
    sum_q1_q2 = cmd.volume_first_quadrimester + cmd.volume_second_quadrimester
    return volume_annual <= 0 or sum_q1_q2 != volume_annual
