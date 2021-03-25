import attr

from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from osis_common.ddd import interface
from workshops_ddd_ue.command import CreatePartimCommand
from workshops_ddd_ue.domain._language import Language
from workshops_ddd_ue.domain._remarks import Remarks
from workshops_ddd_ue.domain.learning_unit_year import LearningUnit
from workshops_ddd_ue.validators.validators_by_business_action import CreatePartimValidatorList


@attr.s(frozen=True, slots=True)
class PartimIdentity(interface.EntityIdentity):
    subdivision = attr.ib(type=str)

    def __str__(self):
        return self.subdivision


class PartimBuilder:
    @classmethod
    def build_from_command(cls, cmd: 'CreatePartimCommand', learning_unit: 'LearningUnit') -> 'Partim':
        CreatePartimValidatorList(
            learning_unit=learning_unit,
            subdivision=cmd.subdivision,
        ).validate()
        return Partim(
            entity_id=PartimIdentity(subdivision=cmd.subdivision),
            title_fr=cmd.title_fr,
            title_en=cmd.title_en,
            credits=cmd.credits,
            periodicity=PeriodicityEnum[cmd.periodicity],
            language=Language(
                ietf_code=None,
                name=None,
                iso_code=cmd.iso_code,
            ),  # FIXME
            remarks=Remarks(
                faculty=cmd.remark_faculty,
                publication_fr=cmd.remark_publication_fr,
                publication_en=cmd.remark_publication_en,
            ),
        )


@attr.s(slots=True, hash=False, eq=False)
class Partim(interface.Entity):
    entity_id = attr.ib(type=PartimIdentity)
    title_fr = attr.ib(type=str)
    title_en = attr.ib(type=str)
    credits = attr.ib(type=int)
    periodicity = attr.ib(type=PeriodicityEnum)
    language = attr.ib(type=Language)
    remarks = attr.ib(type=Remarks)

    @property
    def subdivision(self) -> str:
        return self.entity_id.subdivision
