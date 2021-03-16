import attr

from base.models.enums.entity_type import EntityType
from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from osis_common.ddd import interface


class AcademicYear(interface.ValueObject):
    year = attr.ib(type=int)

    def __str__(self):
        # 2021-22
        return "{}-{}".format(self.year, self.year + 1)


class ResponsibleEntityIdentity(interface.EntityIdentity):
    code = attr.ib(type=str)


class Address(interface.ValueObject):
    country = attr.ib(type=str)
    street_name = attr.ib(type=str)
    street_number = attr.ib(type=str)
    city = attr.ib(type=str)
    postal_code = attr.ib(type=str)


class ResponsibleEntity(interface.Entity):
    entity_id = attr.ib(type=ResponsibleEntityIdentity)
    title = attr.ib(type=str)
    address = attr.ib(type=Address)
    type = attr.ib(type=EntityType)

    @property
    def code(self):
        return self.entity_id.code


class LearningUnitIdentity(interface.EntityIdentity):
    academic_year = attr.ib(type=AcademicYear)
    code = attr.ib(type=str)


class Language(interface.ValueObject):
    ietf_code = attr.ib(type=str)  # FR_BE, EN...
    name = attr.ib(type=str)
    iso_code = attr.ib(type=str)


# class Remark(interface.ValueObject):
#     label = attr.ib(type=str)  # faculty, publication...
#     language = attr.ib(type=Language)
#     content = attr.ib(type=str)


class Remarks(interface.ValueObject):
    faculty = attr.ib(type=str)
    publication_fr = attr.ib(type=str)
    publication_en = attr.ib(type=str)


class Titles(interface.ValueObject):
    common_fr = attr.ib(type=str)
    specific_fr = attr.ib(type=str)
    common_en = attr.ib(type=str)
    specific_en = attr.ib(type=str)


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
    def academic_year(self) -> int:
        return self.entity_id.academic_year
