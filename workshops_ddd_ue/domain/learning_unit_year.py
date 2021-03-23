import attr

from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from osis_common.ddd import interface
from workshops_ddd_ue.domain._academic_year import AcademicYear
from workshops_ddd_ue.domain._language import Language
from workshops_ddd_ue.domain._remarks import Remarks
from workshops_ddd_ue.domain._responsible_entity import ResponsibleEntity
from workshops_ddd_ue.domain._titles import Titles


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
    type = attr.ib(type=LearningContainerYearType)
    internship_subtype = attr.ib(type=InternshipSubtype)
    responsible_entity = attr.ib(type=ResponsibleEntity)
    periodicity = attr.ib(type=PeriodicityEnum)
    language = attr.ib(type=Language)
    remarks = attr.ib(type=Remarks)

    @property
    def academic_year(self) -> 'AcademicYear':
        return self.entity_id.academic_year

    @property
    def code(self) -> str:
        return self.entity_id.code
