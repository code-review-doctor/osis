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

from ddd.logic.attribution.commands import DistributeClassToTutorCommand
from ddd.logic.attribution.domain.model.tutor import Tutor
from ddd.logic.attribution.domain.service.i_tutor_attribution import ITutorAttributionToLearningUnitTranslator
from ddd.logic.attribution.domain.validator.exceptions import AssignedVolumeInvalidValueException, \
    AssignedVolumeTooHighException
from ddd.logic.effective_class_repartition.domain.validator.exceptions import InvalidVolumeException
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from osis_common.ddd import interface

MINIMUM_VALUE = 0


class IsDistributedVolumeCorrect(interface.DomainService):

    @classmethod
    def verify(
            cls,
            cmd: 'DistributeClassToTutorCommand',
            tutor: 'Tutor',
            effective_class: 'EffectiveClass',
            tutor_attribution_translator: 'ITutorAttributionToLearningUnitTranslator',
    ):
        total_class_volume = effective_class.volumes.total_volume
        distributed_volume = cmd.distributed_volume
        attribution_volume = tutor_attribution_translator.get_tutor_attribution_to_learning_unit(
            tutor.entity_id,
            effective_class.entity_id.learning_unit_identity
        ).attributed_volume_to_learning_unit

        if distributed_volume > total_class_volume or distributed_volume < 0:
            raise InvalidVolumeException(total_class_volume)

        if distributed_volume:
            if distributed_volume < MINIMUM_VALUE or distributed_volume > total_class_volume:
                raise AssignedVolumeInvalidValueException(distributed_volume, total_class_volume)
            if distributed_volume > attribution_volume:
                raise AssignedVolumeTooHighException(distributed_volume, attribution_volume)
