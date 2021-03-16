import attr

from base.models.enums.entity_type import EntityType
from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.utils import utils
from osis_common.ddd import interface
from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository
from workshops_ddd_ue.validators.validators_by_business_action import CreateLearningUnitValidatorList


@attr.s(frozen=True, slots=True)
class AcademicYear(interface.ValueObject):
    year = attr.ib(type=int)

    def __str__(self):
        # 2021-22
        return "{}-{}".format(self.year, self.year + 1)


@attr.s(frozen=True, slots=True)
class ResponsibleEntityIdentity(interface.EntityIdentity):
    code = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class Address(interface.ValueObject):
    country = attr.ib(type=str)
    street_name = attr.ib(type=str)
    street_number = attr.ib(type=str)
    city = attr.ib(type=str)
    postal_code = attr.ib(type=str)


@attr.s(slots=True, hash=False, eq=False)
class ResponsibleEntity(interface.Entity):
    entity_id = attr.ib(type=ResponsibleEntityIdentity)
    title = attr.ib(type=str)
    address = attr.ib(type=Address)
    type = attr.ib(type=EntityType)

    @property
    def code(self) -> str:
        return self.entity_id.code



@attr.s(frozen=True, slots=True)
class LearningUnitIdentity(interface.EntityIdentity):
    academic_year = attr.ib(type=AcademicYear)
    code = attr.ib(type=str)

    @property
    def year(self) -> int:
        return self.academic_year.year


@attr.s(frozen=True, slots=True)
class Language(interface.ValueObject):
    ietf_code = attr.ib(type=str)  # FR_BE, EN...
    name = attr.ib(type=str)
    iso_code = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class Remarks(interface.ValueObject):
    faculty = attr.ib(type=str)
    publication_fr = attr.ib(type=str)
    publication_en = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class Titles(interface.ValueObject):
    common_fr = attr.ib(type=str)
    specific_fr = attr.ib(type=str)
    common_en = attr.ib(type=str)
    specific_en = attr.ib(type=str)


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
    def code(self) -> int:
        return self.entity_id.code

    def create(self, command: 'CreateLearningUnitCommand', repository: LearningUnitRepository) -> 'LearningUnit':
        responsible_entity = ResponsibleEntity(
            entity_id=ResponsibleEntityIdentity(code=command.responsible_entity_code),
            title=None,
            address=Address(
                country=None,
                street_name=None,
                street_number=None,
                city=None,
                postal_code=None,
            ),
            type=None,
        )

        CreateLearningUnitValidatorList(repository, responsible_entity, command).validate()

        academic_year = AcademicYear(year=command.academic_year)
        return LearningUnit(
            entity_id=LearningUnitIdentity(code=command.code, academic_year=academic_year),
            titles=Titles(
                common_fr=command.common_title_fr,
                specific_fr=command.specific_title_fr,
                common_en=command.common_title_en,
                specific_en=command.specific_title_en,
            ),
            credits=command.credits,
            type=utils.get_enum_from_str(command.type, LearningContainerYearType),
            internship_subtype=utils.get_enum_from_str(command.internship_subtype, InternshipSubtype),
            responsible_entity=responsible_entity,
            periodicity=utils.get_enum_from_str(command.periodicity, PeriodicityEnum),
            language=Language(
                ietf_code=None,
                name=None,
                iso_code=command.iso_code,
            ),
            remarks=Remarks(
                faculty=command.remark_faculty,
                publication_fr=command.remark_publication_fr,
                publication_en=command.remark_publication_en,
            ),
        )
