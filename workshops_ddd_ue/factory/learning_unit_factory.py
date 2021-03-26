import abc
from typing import List, Type

import attr

from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from osis_common.ddd.interface import CommandRequest, RootEntity
from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain._language import Language
from workshops_ddd_ue.domain._remarks import Remarks
from workshops_ddd_ue.domain.responsible_entity import ResponsibleEntity, ResponsibleEntityIdentity
from workshops_ddd_ue.domain._titles import Titles
from workshops_ddd_ue.domain.learning_unit_year import LearningUnit, LearningUnitIdentity, CourseLearningUnit, \
    InternshipLearningUnit, DissertationLearningUnit, OtherCollectiveLearningUnit, OtherIndividualLearningUnit, \
    MasterThesisLearningUnit, ExternalLearningUnit
from workshops_ddd_ue.dto.learning_unit_dto import DTO, LearningUnitDataDTO
from workshops_ddd_ue.factory.learning_unit_identity_factory import LearningUnitIdentityBuilder
from workshops_ddd_ue.validators.validators_by_business_action import CopyLearningUnitToNextYearValidatorList, \
    CreateLearningUnitValidatorList


# TODO :: to move into osis_common.ddd.interface
class RootEntityBuilder(abc.ABC):

    @classmethod
    def build_from_command(cls, cmd: 'CommandRequest') -> 'RootEntity':
        raise NotImplementedError()

    @classmethod
    def build_from_repository_dto(cls, dto_object: 'DTO') -> 'RootEntity':
        raise NotImplementedError()


class LearningUnitBuilder(RootEntityBuilder):

    @classmethod
    def build(cls, dto: 'LearningUnitDataDTO', all_existing_identities: List['LearningUnitIdentity']) -> 'LearningUnit':
        CreateLearningUnitValidatorList(dto, all_existing_identities).validate()

        return _get_learning_unit_class(dto.type)(
            entity_id=LearningUnitIdentityBuilder.build_from_code_and_year(dto.code, dto.year),
            type=LearningContainerYearType[dto.type],
            titles=_build_titles(
                dto.common_title_fr,
                dto.specific_title_fr,
                dto.common_title_en,
                dto.specific_title_en
            ),
            credits=dto.credits,
            internship_subtype=InternshipSubtype[dto.internship_subtype],
            responsible_entity=ResponsibleEntity(
                entity_id=ResponsibleEntityIdentity(dto.responsible_entity_code),
                type=dto.responsible_entity_type
            ),
            periodicity=PeriodicityEnum[dto.periodicity],
            language=_build_language(dto.iso_code),
            remarks=_build_remarks(dto.remark_faculty, dto.remark_publication_fr, dto.remark_publication_en),
        )

    @classmethod
    def copy_to_next_year(
            cls,
            learning_unit: 'LearningUnit',
            all_existing_lear_unit_identities: List['LearningUnitIdentity']
    ) -> 'LearningUnit':
        CopyLearningUnitToNextYearValidatorList(learning_unit.entity_id, all_existing_lear_unit_identities).validate()
        learning_unit_next_year = attr.evolve(
            learning_unit,
            entity_id=LearningUnitIdentityBuilder.build_for_next_year(learning_unit.entity_id)
        )
        return learning_unit_next_year


def _get_learning_unit_class(type: str) -> Type[LearningUnit]:
    if type == LearningContainerYearType.COURSE.name:
        return CourseLearningUnit
    if type == LearningContainerYearType.INTERNSHIP.name:
        return InternshipLearningUnit
    if type == LearningContainerYearType.DISSERTATION.name:
        return DissertationLearningUnit
    if type == LearningContainerYearType.OTHER_COLLECTIVE.name:
        return OtherCollectiveLearningUnit
    if type == LearningContainerYearType.OTHER_INDIVIDUAL.name:
        return OtherIndividualLearningUnit
    if type == LearningContainerYearType.MASTER_THESIS.name:
        return MasterThesisLearningUnit
    if type == LearningContainerYearType.EXTERNAL.name:
        return ExternalLearningUnit


def _build_remarks(remark_faculty: str, remark_publication_fr: str, remark_publication_en: str):
    return Remarks(
        faculty=remark_faculty,
        publication_fr=remark_publication_fr,
        publication_en=remark_publication_en,
    )


def _build_language(iso_code: str):
    return Language(  # FIXME
        ietf_code=None,
        name=None,
        iso_code=iso_code,
    )


# def _build_responsible_entity(responsible_entity_code: str):
#     return ResponsibleEntity(  # FIXME
#         entity_id=ResponsibleEntityIdentity(code=responsible_entity_code),
#         type=None,
#     )


def _build_titles(common_title_fr: str, specific_title_fr: str, common_title_en: str, specific_title_en: str):
    return Titles(
        common_fr=common_title_fr,
        specific_fr=specific_title_fr,
        common_en=common_title_en,
        specific_en=specific_title_en,
    )
