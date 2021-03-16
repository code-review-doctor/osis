import attr

from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.utils import utils
from osis_common.ddd import interface
from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain._academic_year import AcademicYear
from workshops_ddd_ue.domain._address import Address
from workshops_ddd_ue.domain._language import Language
from workshops_ddd_ue.domain._remarks import Remarks
from workshops_ddd_ue.domain._responsible_entity import ResponsibleEntityIdentity, ResponsibleEntity
from workshops_ddd_ue.domain._titles import Titles
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository
from workshops_ddd_ue.validators.validators_by_business_action import CreateLearningUnitValidatorList


@attr.s(frozen=True, slots=True)
class LearningUnitIdentity(interface.EntityIdentity):
    academic_year = attr.ib(type=AcademicYear)
    code = attr.ib(type=str)

    @property
    def year(self) -> int:
        return self.academic_year.year


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

    @staticmethod
    def create(command: 'CreateLearningUnitCommand', repository: LearningUnitRepository) -> 'LearningUnit':
        responsible_entity = ResponsibleEntity(  # FIXME
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
            language=Language(  # FIXME
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
