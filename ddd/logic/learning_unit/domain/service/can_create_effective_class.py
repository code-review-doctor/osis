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
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from ddd.logic.learning_unit.domain.validator.exceptions import ClassTypeInvalidException, \
    LearningUnitHasPartimException, LearningUnitHasProposalException, \
    LearningUnitHasEnrollmentException, AnnualVolumeInvalidException, CodeClassAlreadyExistForUeException
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository
from osis_common.ddd import interface


class CanCreateEffectiveClass(interface.DomainService):

    @classmethod
    def check(
            cls,
            learning_unit: 'LearningUnit',
            learning_unit_repository: 'ILearningUnitRepository',
            cmd: 'CreateEffectiveClassCommand',
            all_existing_class_identities: List['EffectiveClassIdentity']
    ):
        exceptions = set()  # type Set[BusinessException]
        if learning_unit.is_external():
            exceptions.add(ClassTypeInvalidException())

        if learning_unit.has_partim():
            exceptions.add(LearningUnitHasPartimException())

        if learning_unit_repository.has_proposal(learning_unit):
            exceptions.add(LearningUnitHasProposalException())

        if learning_unit_repository.has_enrollments(learning_unit):
            exceptions.add(LearningUnitHasEnrollmentException())

        if _is_effective_class_volumes_inconsistent_with_learning_unit_volume_annual(learning_unit, cmd):
            exceptions.add(AnnualVolumeInvalidException())

        if all_existing_class_identities:
            for id in all_existing_class_identities:
                if id.learning_unit_identity == learning_unit.entity_id and id.class_code == cmd.class_code:
                    exceptions.add(CodeClassAlreadyExistForUeException(learning_unit.entity_id, cmd.class_code))

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)


def _is_effective_class_volumes_inconsistent_with_learning_unit_volume_annual(
        learning_unit: 'LearningUnit',
        cmd: 'CreateEffectiveClassCommand'
) -> Decimal:
    practical_volumes = learning_unit.practical_part.volumes
    lecturing_volumes = learning_unit.lecturing_part.volumes
    if practical_volumes.volume_annual > 0 and not lecturing_volumes.volume_annual > 0:
        volume_annual = practical_volumes.volume_annual
    else:
        volume_annual = lecturing_volumes.volume_annual
    sum_q1_q2 = cmd.volume_first_quadrimester + cmd.volume_second_quadrimester
    return volume_annual <= 0 or sum_q1_q2 != volume_annual
