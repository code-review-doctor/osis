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
from typing import Union, Type

from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.domain.model._campus import TeachingPlace
from ddd.logic.learning_unit.domain.model._class_titles import ClassTitles
from ddd.logic.learning_unit.domain.model._volumes_repartition import Volumes
from ddd.logic.learning_unit.domain.model.effective_class import PracticalEffectiveClass, \
    LecturingEffectiveClass, EffectiveClass
from ddd.logic.learning_unit.dtos import EffectiveClassFromRepositoryDTO
from osis_common.ddd import interface
from osis_common.ddd.interface import CommandRequest


class EffectiveClassBuilder(interface.RootEntityBuilder):
    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> Union['PracticalEffectiveClass', 'LecturingEffectiveClass']:
        raise NotImplementedError

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'EffectiveClassFromRepositoryDTO') -> 'EffectiveClass':
        class_identity = EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
            code=dto_object.code,
            learning_unit_code=dto_object.learning_unit_code,
            learning_unit_year=dto_object.learning_unit_year
        )
        return _get_effective_class_type_with_dto(dto_object)(
            entity_id=class_identity,
            titles=ClassTitles(
                fr=dto_object.title_fr,
                en=dto_object.title_en
            ),
            teaching_place=TeachingPlace(
                place=dto_object.teaching_place,
                organization_name=dto_object.teaching_organization
            ),
            derogation_quadrimester=DerogationQuadrimester(dto_object.derogation_quadrimester),
            session_derogation=dto_object.session_derogation,
            volumes=Volumes(
                volume_first_quadrimester=dto_object.volume_q1,
                volume_second_quadrimester=dto_object.volume_q2,
                volume_annual=dto_object.volume_annual
            )
        )


def _get_effective_class_type_with_dto(
        dto_object: 'EffectiveClassFromRepositoryDTO'
) -> Type['EffectiveClass']:
    return PracticalEffectiveClass if dto_object.volume_q2 > 0 and not dto_object.volume_q1 > 0 \
        else LecturingEffectiveClass
