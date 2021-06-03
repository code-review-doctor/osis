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
from functools import partial
from typing import List

from base.ddd.utils.business_validator import execute_functions_and_aggregate_exceptions
from ddd.logic.learning_unit.builder.effective_class_builder import EffectiveClassBuilder
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand, UpdateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity, EffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from ddd.logic.learning_unit.domain.validator.exceptions import CodeClassAlreadyExistForUeException, \
    AnnualVolumeInvalidException
from osis_common.ddd import interface


class SaveEffectiveClass(interface.DomainService):

    @classmethod
    def create(
            cls,
            learning_unit: 'LearningUnit',
            cmd: 'CreateEffectiveClassCommand',
            all_existing_class_identities: List['EffectiveClassIdentity'],
    ):
        volumes_consistency_with_learning_unit = partial(
            _raise_if_class_volumes_inconsistent_with_learning_unit_volumes,
            learning_unit,
            cmd.volume_first_quadrimester,
            cmd.volume_second_quadrimester
        )
        __, effective_class = execute_functions_and_aggregate_exceptions(
            volumes_consistency_with_learning_unit,
            partial(_raise_if_class_code_already_exists, all_existing_class_identities, cmd.class_code, learning_unit),
            partial(EffectiveClassBuilder.build_from_command, cmd, learning_unit),
        )

        return effective_class

    @classmethod
    def update(
            cls,
            learning_unit: 'LearningUnit',
            effective_class: 'EffectiveClass',
            cmd: 'UpdateEffectiveClassCommand',
            all_existing_class_identities: List['EffectiveClassIdentity'],
    ) -> None:
        volumes_consistency_with_learning_unit = partial(
            _raise_if_class_volumes_inconsistent_with_learning_unit_volumes,
            learning_unit,
            cmd.volume_first_quadrimester,
            cmd.volume_second_quadrimester
        )
        execute_functions_and_aggregate_exceptions(
            volumes_consistency_with_learning_unit,
            partial(_raise_if_class_code_already_exists, all_existing_class_identities, cmd.class_code, learning_unit),
            partial(effective_class.update, cmd),
        )


def _raise_if_class_code_already_exists(all_existing_class_identities, class_code: str, learning_unit):
    if all_existing_class_identities:
        for class_id in all_existing_class_identities:
            if class_id.learning_unit_identity == learning_unit.entity_id and class_id.class_code == class_code:
                raise CodeClassAlreadyExistForUeException(learning_unit.entity_id, class_code)


def _raise_if_class_volumes_inconsistent_with_learning_unit_volumes(
        learning_unit: 'LearningUnit',
        volume_first_quadrimester: float,
        volume_second_quadrimester: float
) -> None:
    practical_part = learning_unit.practical_part
    lecturing_part = learning_unit.lecturing_part

    if practical_part and not lecturing_part:
        volume_annual = practical_part.volumes.volume_annual
    else:
        volume_annual = lecturing_part.volumes.volume_annual

    sum_q1_q2 = volume_first_quadrimester + volume_second_quadrimester
    if volume_annual <= 0 or sum_q1_q2 != volume_annual:
        raise AnnualVolumeInvalidException(learning_unit)
