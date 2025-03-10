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

from base.ddd.utils.business_validator import execute_functions_and_aggregate_exceptions
from ddd.logic.application.domain.service.i_learning_unit_service import ILearningUnitService
from ddd.logic.effective_class_repartition.domain.validator.exceptions import AssignedVolumeInvalidValueException
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.domain.model._financial_volumes_repartition import DurationUnit
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from osis_common.ddd import interface

MINIMUM_VALUE = 0


class DistributedVolumeWithClassVolume(interface.DomainService):

    @classmethod
    def verify(
            cls,
            distributed_volume: 'DurationUnit',
            effective_class: 'EffectiveClass',
            learning_unit_service: ILearningUnitService,
    ):
        learning_unit_id = LearningUnitIdentityBuilder.build_from_code_and_year(
            effective_class.learning_unit_identity.code,
            effective_class.learning_unit_identity.year
        )
        learning_unit = learning_unit_service.search_learning_unit_annual_volume_dto(learning_unit_id)
        class_tot_vol = effective_class.volumes.total_volume
        total_class_volume = class_tot_vol \
            if class_tot_vol and class_tot_vol > 0 else learning_unit.volume
        if distributed_volume:
            execute_functions_and_aggregate_exceptions(
                partial(_should_be_lower_than_effective_class_volume, distributed_volume, total_class_volume),
            )


def _should_be_lower_than_effective_class_volume(distributed_volume, total_class_volume):
    if distributed_volume and distributed_volume < MINIMUM_VALUE or distributed_volume > total_class_volume:
        raise AssignedVolumeInvalidValueException(distributed_volume, total_class_volume)
