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
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.effective_class_repartition.domain.service.i_tutor_attribution import \
    ITutorAttributionToLearningUnitTranslator
from ddd.logic.effective_class_repartition.domain.validator.exceptions import AssignedVolumeInvalidValueException, \
    AssignedVolumeTooHighException, InvalidVolumeException
from ddd.logic.learning_unit.domain.model._financial_volumes_repartition import DurationUnit
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from osis_common.ddd import interface

MINIMUM_VALUE = 0


class IsDistributedVolumeCorrect(interface.DomainService):

    @classmethod
    def verify(
            cls,
            distributed_volume: 'DurationUnit',
            attribution_uuid: str,
            effective_class: 'EffectiveClass',
            tutor_attribution_translator: 'ITutorAttributionToLearningUnitTranslator',
    ):
        total_class_volume = effective_class.volumes.total_volume
        attribution = tutor_attribution_translator.get_learning_unit_attribution(attribution_uuid)
        if effective_class.is_lecturing:
            attribution_volume = attribution.lecturing_volume_attributed
        else:
            attribution_volume = attribution.practical_volume_attributed

        exceptions = set()

        if distributed_volume:
            if distributed_volume < MINIMUM_VALUE or distributed_volume > total_class_volume:
                exceptions.add(AssignedVolumeInvalidValueException(distributed_volume, total_class_volume))
            if distributed_volume > attribution_volume:
                exceptions.add(AssignedVolumeTooHighException(distributed_volume, attribution_volume))
            if distributed_volume > total_class_volume or distributed_volume <= 0:
                exceptions.add(InvalidVolumeException(total_class_volume))

        if exceptions:
            raise MultipleBusinessExceptions(exceptions=exceptions)
