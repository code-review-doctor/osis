import abc
from typing import Union

from osis_common.ddd.interface import CommandRequest, EntityIdentity
from workshops_ddd_ue.command import CopyLearningUnitToNextYearCommand
from workshops_ddd_ue.domain._academic_year import AcademicYear
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity
from workshops_ddd_ue.dto.learning_unit_dto import DTO


# TODO :: to move into osis_common.ddd.interface


class EntityIdentityBuilder(abc.ABC):

    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'EntityIdentity':
        raise NotImplementedError()

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'DTO') -> 'EntityIdentity':
        raise NotImplementedError()


class LearningUnitIdentityBuilder(EntityIdentityBuilder):

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
