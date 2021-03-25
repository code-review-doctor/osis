import abc
from typing import Union

from osis_common.ddd.interface import CommandRequest, EntityIdentity, EntityIdentityBuilder
from workshops_ddd_ue.command import CopyLearningUnitToNextYearCommand
from workshops_ddd_ue.domain._academic_year import AcademicYear
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity
from workshops_ddd_ue.domain.responsible_entity import ResponsibleEntityIdentity
from workshops_ddd_ue.dto.learning_unit_dto import DTO


class ResponsibleEntityIdentityBuilder(EntityIdentityBuilder):

    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'EntityIdentity':
        pass

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'DTO') -> 'EntityIdentity':
        pass

    @classmethod
    def build_from_code(cls, code: str) -> 'ResponsibleEntityIdentity':
        return ResponsibleEntityIdentity(code=code)
