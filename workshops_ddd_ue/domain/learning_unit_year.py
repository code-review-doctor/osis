from typing import List

import attr

from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from osis_common.ddd import interface
from workshops_ddd_ue.command import CreatePartimCommand
from workshops_ddd_ue.domain._academic_year import AcademicYear
from workshops_ddd_ue.domain._language import Language
from workshops_ddd_ue.domain._remarks import Remarks
from workshops_ddd_ue.domain._responsible_entity import ResponsibleEntity
from workshops_ddd_ue.domain._titles import Titles
from workshops_ddd_ue.domain._partim import Partim, PartimBuilder
from workshops_ddd_ue.validators.validators_by_business_action import CreatePartimValidatorList


@attr.s(frozen=True, slots=True)
class LearningUnitIdentity(interface.EntityIdentity):
    academic_year = attr.ib(type=AcademicYear)
    code = attr.ib(type=str)

    def __str__(self):
        return "{} - ({})".format(self.code, self.academic_year)

    @property
    def year(self) -> int:
        return self.academic_year.year

    def get_next_year(self):
        return self.year + 1


@attr.s(slots=True, hash=False, eq=False)
class LearningUnit(interface.RootEntity):
    entity_id = attr.ib(type=LearningUnitIdentity)
    titles = attr.ib(type=Titles)
    credits = attr.ib(type=int)
    internship_subtype = attr.ib(type=InternshipSubtype)
    responsible_entity = attr.ib(type=ResponsibleEntity)
    periodicity = attr.ib(type=PeriodicityEnum)
    language = attr.ib(type=Language)
    remarks = attr.ib(type=Remarks)
    partims = attr.ib(type=List[Partim])

    @property
    def academic_year(self) -> 'AcademicYear':
        return self.entity_id.academic_year

    @property
    def code(self) -> str:
        return self.entity_id.code

    def contains_partim_subdivision(self, subdivision: str) -> bool:
        return subdivision in {p.subdivision for p in self.partims}

    def create_partim(self, create_partim_cmd: 'CreatePartimCommand') -> None:
        partim = PartimBuilder.build_from_command(
            cmd=create_partim_cmd,
            learning_unit=self,
        )
        self.partims.append(partim)


class CourseLearningUnit(LearningUnit):
    type = LearningContainerYearType.COURSE


class InternshipLearningUnit(LearningUnit):
    type = LearningContainerYearType.INTERNSHIP


class DissertationLearningUnit(LearningUnit):
    type = LearningContainerYearType.DISSERTATION


class OtherCollectiveLearningUnit(LearningUnit):
    type = LearningContainerYearType.OTHER_COLLECTIVE


class OtherIndividualLearningUnit(LearningUnit):
    type = LearningContainerYearType.OTHER_INDIVIDUAL


class MasterThesisLearningUnit(LearningUnit):
    type = LearningContainerYearType.MASTER_THESIS


class ExternalLearningUnit(LearningUnit):
    type = LearningContainerYearType.EXTERNAL
