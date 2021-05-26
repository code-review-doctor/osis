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
from typing import Type, Union, List

from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.domain.model._campus import TeachingPlace
from ddd.logic.learning_unit.domain.model._class_titles import ClassTitles
from ddd.logic.learning_unit.domain.model._volumes_repartition import Volumes
from ddd.logic.learning_unit.domain.model.effective_class import PracticalEffectiveClass, \
    LecturingEffectiveClass, EffectiveClass, EffectiveClassIdentity
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit
from ddd.logic.learning_unit.domain.validator.validators_by_business_action import CreateEffectiveClassValidatorList
from osis_common.ddd import interface
from osis_common.ddd.interface import DTO


class EffectiveClassBuilder(interface.RootEntityBuilder):
    @classmethod
    def build_from_command(
            cls,
            cmd: 'CreateEffectiveClassCommand',
            learning_unit: LearningUnit,
            all_existing_class_identities: List['EffectiveClassIdentity']
    ) -> Union['PracticalEffectiveClass', 'LecturingEffectiveClass']:
        CreateEffectiveClassValidatorList(
            command=cmd,
            learning_unit=learning_unit,
            all_existing_class_identities=all_existing_class_identities
        ).validate()

        effective_class_identity = EffectiveClassIdentityBuilder.build_from_command(cmd)

        return _define_effective_class_type(learning_unit)(
            entity_id=effective_class_identity,
            titles=ClassTitles(fr=cmd.title_fr, en=cmd.title_en),
            teaching_place=TeachingPlace(place=cmd.place, organization_name=cmd.organization_name),
            derogation_quadrimester=DerogationQuadrimester(cmd.derogation_quadrimester),
            session_derogation=DerogationSession(cmd.session_derogation),
            volumes=Volumes(
                volume_first_quadrimester=cmd.volume_first_quadrimester,
                volume_second_quadrimester=cmd.volume_second_quadrimester,
                volume_annual=cmd.volume_annual
                )
            )

    @classmethod
    def build_from_repository_dto(
            cls,
            dto_object: 'DTO'
    ) -> Union['PracticalEffectiveClass', 'LecturingEffectiveClass']:
        raise NotImplementedError


def _define_effective_class_type(learning_unit: LearningUnit) -> Type[EffectiveClass]:
    class_type = None
    lecturing_annual_volume = learning_unit.lecturing_part.volumes.volume_annual
    practical_annual_volume = learning_unit.practical_part.volumes.volume_annual
    if lecturing_annual_volume > 0.0 and practical_annual_volume > 0.0:
        class_type = LecturingEffectiveClass
    elif lecturing_annual_volume > 0.0:
        class_type = LecturingEffectiveClass
    elif practical_annual_volume > 0.0:
        class_type = PracticalEffectiveClass
    return class_type
