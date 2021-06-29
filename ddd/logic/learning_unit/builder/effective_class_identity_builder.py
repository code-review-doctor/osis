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
from typing import Union

from ddd.logic.attribution.commands import DistributeClassToTutorCommand
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand, UpdateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity, EffectiveClassCode
from osis_common.ddd.interface import EntityIdentityBuilder, DTO


class EffectiveClassIdentityBuilder(EntityIdentityBuilder):
    @classmethod
    def build_from_command(
            cls,
            cmd: Union['CreateEffectiveClassCommand', 'UpdateEffectiveClassCommand', 'DistributeClassToTutorCommand']
    ) -> 'EffectiveClassIdentity':
        return EffectiveClassIdentity(
            class_code=cmd.class_code,
            learning_unit_identity=LearningUnitIdentityBuilder.build_from_code_and_year(
                code=cmd.learning_unit_code,
                year=cmd.year
            )
        )

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'DTO') -> 'EffectiveClassIdentity':
        raise NotImplementedError

    @classmethod
    def build_from_code_and_learning_unit_identity_data(
            cls,
            class_code: EffectiveClassCode,
            learning_unit_code: str,
            learning_unit_year: int
    ) -> 'EffectiveClassIdentity':
        learning_unit_identity = LearningUnitIdentityBuilder.build_from_code_and_year(
            code=learning_unit_code,
            year=learning_unit_year
        )
        return EffectiveClassIdentity(class_code=class_code, learning_unit_identity=learning_unit_identity)
