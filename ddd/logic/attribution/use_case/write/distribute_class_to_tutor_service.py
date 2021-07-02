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
from ddd.logic.attribution.builder.tutor_builder import TutorBuilder
from ddd.logic.attribution.builder.tutor_identity_builder import TutorIdentityBuilder
from ddd.logic.attribution.commands import DistributeClassToTutorCommand
from ddd.logic.attribution.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.attribution.domain.model._learning_unit_attribution import LearningUnitAttributionIdentity
from ddd.logic.attribution.domain.model.tutor import TutorIdentity
from ddd.logic.attribution.repository.i_tutor import ITutorRepository
from ddd.logic.effective_class_repartition.domain.validator.validators_by_business_action import \
    DistributeClassToTutorValidatorList
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.repository.i_effective_class import IEffectiveClassRepository


def distribute_class_to_tutor(
        cmd: DistributeClassToTutorCommand,
        repository: 'ITutorRepository',
        effective_class_repository: 'IEffectiveClassRepository'
) -> 'TutorIdentity':
    # TODO: to implement
    # TODO: reuse check_class_belongs_to_learning_unit DomainService
    tutor_identity = TutorIdentityBuilder.build_from_personal_id_number(cmd.tutor_personal_id_number)
    tutor = repository.get(tutor_identity)
    if not tutor:
        # first_attribution_to_class
        tutor = TutorBuilder.build_from_command(cmd)

    class_volume = _build_class_volume_repartition(cmd)
    tutor.assign_class(class_volume)

    effective_class = effective_class_repository.get(EffectiveClassIdentityBuilder.build_from_command(cmd))
    DistributeClassToTutorValidatorList(cmd, effective_class).validate()
    repository.save(tutor)
    return tutor.entity_id


def _build_class_volume_repartition(cmd):
    return ClassVolumeRepartition(
        effective_class=EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
            class_code=cmd.class_code,
            learning_unit_year=cmd.year,
            learning_unit_code=cmd.learning_unit_code),
        distributed_volume=cmd.distributed_volume,
        attribution=LearningUnitAttributionIdentity(uuid=cmd.learning_unit_attribution_uuid)
    )
