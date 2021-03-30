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
