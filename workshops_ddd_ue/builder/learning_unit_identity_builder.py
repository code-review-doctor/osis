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

from osis_common.ddd.interface import EntityIdentityBuilder, DTO, EntityIdentity
from workshops_ddd_ue.business_types import *
from workshops_ddd_ue.command import CopyLearningUnitToNextYearCommand
from workshops_ddd_ue.domain._academic_year import AcademicYear


class LearningUnitIdentityBuilder(EntityIdentityBuilder):

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'DTO') -> 'EntityIdentity':
        raise NotImplementedError

    @classmethod
    def build_from_command(cls, cmd: Union[CopyLearningUnitToNextYearCommand]) -> 'LearningUnitIdentity':
        return cls.build_from_code_and_year(cmd.copy_from_code, cmd.copy_from_year)

    @classmethod
    def build_for_next_year(cls, learning_unit_identity: 'LearningUnitIdentity') -> 'LearningUnitIdentity':
        return cls.build_from_code_and_year(learning_unit_identity.code, learning_unit_identity.get_next_year())

    @classmethod
    def build_from_code_and_year(cls, code: str, year: int) -> 'LearningUnitIdentity':
        return LearningUnitIdentity(
            academic_year=AcademicYear(year=year),
            code=code,
        )
