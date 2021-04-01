##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List, Type

import attr

from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from osis_common.ddd.interface import RootEntityBuilder
from workshops_ddd_ue.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain._language import Language
from workshops_ddd_ue.domain._remarks import Remarks
from workshops_ddd_ue.domain._titles import Titles
from workshops_ddd_ue.domain.learning_unit import LearningUnit, LearningUnitIdentity, CourseLearningUnit, \
    InternshipLearningUnit, DissertationLearningUnit, OtherCollectiveLearningUnit, OtherIndividualLearningUnit, \
    MasterThesisLearningUnit, ExternalLearningUnit
from workshops_ddd_ue.domain.responsible_entity import ResponsibleEntity, ResponsibleEntityIdentity
from workshops_ddd_ue.dto.learning_unit_dto import LearningUnitFromRepositoryDTO
from workshops_ddd_ue.validators.validators_by_business_action import CopyLearningUnitToNextYearValidatorList, \
    CreateLearningUnitValidatorList


class LearningUnitBuilder(RootEntityBuilder):

    @classmethod
    def build_from_command(
            cls,
            cmd: 'CreateLearningUnitCommand',
            all_existing_identities: List['LearningUnitIdentity'],
            responsible_entity_identity: ResponsibleEntityIdentity
    ) -> 'LearningUnit':
        CreateLearningUnitValidatorList(
            command=cmd,
            all_existing_identities=all_existing_identities
        ).validate()
        dto = cmd
        return _get_learning_unit_class(dto.type)(
            entity_id=LearningUnitIdentityBuilder.build_from_code_and_year(dto.code, dto.academic_year),
            titles=_build_titles(
                dto.common_title_fr,
                dto.specific_title_fr,
                dto.common_title_en,
                dto.specific_title_en
            ),
            credits=dto.credits,
            internship_subtype=InternshipSubtype[dto.internship_subtype],
            responsible_entity_identity=responsible_entity_identity,
            periodicity=PeriodicityEnum[dto.periodicity],
            language=_build_language(dto.iso_code),
            remarks=_build_remarks(dto.remark_faculty, dto.remark_publication_fr, dto.remark_publication_en),
        )

    @classmethod
    def build_from_repository_dto(
            cls,
            dto: 'LearningUnitFromRepositoryDTO',
            responsible_entity: 'ResponsibleEntity'
    ) -> 'LearningUnit':
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
            responsible_entity_identity=_build_responsible_entity(dto.responsible_entity_code),
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
