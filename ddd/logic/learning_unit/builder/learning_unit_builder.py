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
from decimal import Decimal
from typing import List, Type, Union, Optional

import attr

from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import PeriodicityEnum
from base.models.enums.learning_unit_year_session import DerogationSession
from base.models.enums.quadrimesters import DerogationQuadrimester
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.builder.ucl_entity_identity_builder import UclEntityIdentityBuilder
from ddd.logic.learning_unit.commands import CreateLearningUnitCommand
from ddd.logic.learning_unit.domain.model._financial_volumes_repartition import FinancialVolumesRepartition
from ddd.logic.learning_unit.domain.model._mobility import Mobility
from ddd.logic.learning_unit.domain.model._partim import PartimBuilder
from ddd.logic.learning_unit.domain.model._remarks import Remarks
from ddd.logic.learning_unit.domain.model._titles import Titles
from ddd.logic.learning_unit.domain.model._volumes_repartition import PracticalPart, LecturingPart, Volumes
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnit, LearningUnitIdentity, CourseLearningUnit, \
    InternshipLearningUnit, DissertationLearningUnit, OtherCollectiveLearningUnit, OtherIndividualLearningUnit, \
    MasterThesisLearningUnit, ExternalLearningUnit
from ddd.logic.learning_unit.domain.model.responsible_entity import UCLEntityIdentity
from ddd.logic.learning_unit.domain.validator.validators_by_business_action import \
    CopyLearningUnitToNextYearValidatorList, \
    CreateLearningUnitValidatorList
from ddd.logic.learning_unit.dtos import LearningUnitFromRepositoryDTO, EntityCode
from ddd.logic.shared_kernel.campus.builder.uclouvain_campus_identity_builder import UclouvainCampusIdentityBuilder
from ddd.logic.shared_kernel.language.builder.language_identity_builder import LanguageIdentityBuilder
from ddd.logic.shared_kernel.language.domain.model.language import LanguageIdentity
from osis_common.ddd.interface import RootEntityBuilder


class LearningUnitBuilder(RootEntityBuilder):

    @classmethod
    def build_from_command(
            cls,
            cmd: 'CreateLearningUnitCommand',
            all_existing_identities: List['LearningUnitIdentity'],
            responsible_entity_identity: UCLEntityIdentity
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
            internship_subtype=InternshipSubtype[dto.internship_subtype] if dto.internship_subtype else None,
            responsible_entity_identity=responsible_entity_identity,
            attribution_entity_identity=None,  # TODO :: to implement and unit test
            periodicity=PeriodicityEnum[dto.periodicity],
            language_id=_build_language(dto.iso_code),
            remarks=_build_remarks(dto.remark_faculty, dto.remark_publication_fr, dto.remark_publication_en),
            lecturing_part=_build_part(
                part_type=LECTURING,
                volume_q1=dto.lecturing_volume_q1,
                volume_q2=dto.lecturing_volume_q2,
                volume_annual=dto.lecturing_volume_annual,
                planned_classes=None,  # TODO :: to implement and unit test
                repartition_entity_1=responsible_entity_identity,
                repartition_entity_2=None,  # TODO :: to implement and unit test
                repartition_entity_3=None,  # TODO :: to implement and unit test
                repartition_volume_entity_1=None,  # TODO :: to implement and unit test
                repartition_volume_entity_2=None,  # TODO :: to implement and unit test
                repartition_volume_entity_3=None,  # TODO :: to implement and unit test
            ),
            practical_part=_build_part(
                part_type=PRACTICAL_EXERCISES,
                volume_q1=dto.practical_volume_q1,
                volume_q2=dto.practical_volume_q2,
                volume_annual=dto.practical_volume_annual,
                planned_classes=None,  # TODO :: to implement and unit test
                repartition_entity_1=responsible_entity_identity,
                repartition_entity_2=None,  # TODO :: to implement and unit test
                repartition_entity_3=None,  # TODO :: to implement and unit test
                repartition_volume_entity_1=None,  # TODO :: to implement and unit test
                repartition_volume_entity_2=None,  # TODO :: to implement and unit test
                repartition_volume_entity_3=None,  # TODO :: to implement and unit test
            ),
            derogation_quadrimester=DerogationQuadrimester[dto.derogation_quadrimester],
            derogation_session=None,  # TODO :: to implement and unit test
            partims=[],
            teaching_place=UclouvainCampusIdentityBuilder.build_from_uuid(dto.teaching_place_uuid),
            professional_integration=False,  # TODO :: to implement and unit test
            is_active=False,  # TODO :: to implement and unit test
            individual_loan=False,
            mobility=_build_mobility(False, False, False),
            stage_dimona=False,
        )

    @classmethod
    def build_from_repository_dto(
            cls,
            dto: 'LearningUnitFromRepositoryDTO',
    ) -> 'LearningUnit':
        attribution_entity = None
        if dto.attribution_entity_code:
            attribution_entity = UclEntityIdentityBuilder.build_from_code(dto.attribution_entity_code)
        derogation_session = None
        if dto.derogation_session:
            enum_key = next(key for key, value in DerogationSession.choices() if value == dto.derogation_session)
            derogation_session = DerogationSession[enum_key]
        return _get_learning_unit_class(dto.type)(
            entity_id=LearningUnitIdentityBuilder.build_from_code_and_year(dto.code, dto.year),
            titles=_build_titles(
                dto.common_title_fr,
                dto.specific_title_fr,
                dto.common_title_en,
                dto.specific_title_en
            ),
            credits=dto.credits,
            internship_subtype=InternshipSubtype[dto.internship_subtype] if dto.internship_subtype else None,
            responsible_entity_identity=UclEntityIdentityBuilder.build_from_code(dto.responsible_entity_code),
            attribution_entity_identity=attribution_entity,
            periodicity=PeriodicityEnum[dto.periodicity],
            language_id=_build_language(dto.iso_code),
            remarks=_build_remarks(dto.remark_faculty, dto.remark_publication_fr, dto.remark_publication_en),
            lecturing_part=_build_part(
                part_type=LECTURING,
                volume_q1=dto.lecturing_volume_q1,
                volume_q2=dto.lecturing_volume_q2,
                volume_annual=dto.lecturing_volume_annual,
                planned_classes=dto.lecturing_planned_classes,
                repartition_entity_1=dto.responsible_entity_code,
                repartition_entity_2=dto.repartition_entity_2,
                repartition_entity_3=dto.repartition_entity_3,
                repartition_volume_entity_1=dto.lecturing_volume_repartition_responsible_entity,
                repartition_volume_entity_2=dto.lecturing_volume_repartition_entity_2,
                repartition_volume_entity_3=dto.lecturing_volume_repartition_entity_3,
            ),
            practical_part=_build_part(
                part_type=PRACTICAL_EXERCISES,
                volume_q1=dto.practical_volume_q1,
                volume_q2=dto.practical_volume_q2,
                volume_annual=dto.practical_volume_annual,
                planned_classes=dto.practical_planned_classes,
                repartition_entity_1=dto.responsible_entity_code,
                repartition_entity_2=dto.repartition_entity_2,
                repartition_entity_3=dto.repartition_entity_3,
                repartition_volume_entity_1=dto.practical_volume_repartition_responsible_entity,
                repartition_volume_entity_2=dto.practical_volume_repartition_entity_2,
                repartition_volume_entity_3=dto.practical_volume_repartition_entity_3,
            ),
            derogation_quadrimester=DerogationQuadrimester[dto.derogation_quadrimester]
            if dto.derogation_quadrimester else None,
            derogation_session=derogation_session,
            partims=[
                PartimBuilder.build_from_dto(partim_dto) for partim_dto in dto.partims
            ],
            teaching_place=UclouvainCampusIdentityBuilder.build_from_uuid(dto.teaching_place_uuid),
            professional_integration=dto.professional_integration,
            is_active=dto.is_active,
            individual_loan=dto.individual_loan,
            mobility=_build_mobility(
                english_friendly=dto.english_friendly,
                french_friendly=dto.french_friendly,
                exchange_students=dto.exchange_students
            ),
            stage_dimona=dto.stage_dimona,
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
    subclass = None
    if type == LearningContainerYearType.COURSE.name:
        subclass = CourseLearningUnit
    elif type == LearningContainerYearType.INTERNSHIP.name:
        subclass = InternshipLearningUnit
    elif type == LearningContainerYearType.DISSERTATION.name:
        subclass = DissertationLearningUnit
    elif type == LearningContainerYearType.OTHER_COLLECTIVE.name:
        subclass = OtherCollectiveLearningUnit
    elif type == LearningContainerYearType.OTHER_INDIVIDUAL.name:
        subclass = OtherIndividualLearningUnit
    elif type == LearningContainerYearType.MASTER_THESIS.name:
        subclass = MasterThesisLearningUnit
    elif type == LearningContainerYearType.EXTERNAL.name:
        subclass = ExternalLearningUnit
    return subclass


def _build_remarks(remark_faculty: str, remark_publication_fr: str, remark_publication_en: str) -> 'Remarks':
    return Remarks(
        faculty=remark_faculty,
        publication_fr=remark_publication_fr,
        publication_en=remark_publication_en,
    )


def _build_language(iso_code: str) -> 'LanguageIdentity':
    return LanguageIdentityBuilder.build_from_code_iso(iso_code)


def _build_titles(
        common_title_fr: str,
        specific_title_fr: str,
        common_title_en: str,
        specific_title_en: str
) -> 'Titles':
    return Titles(
        common_fr=common_title_fr,
        specific_fr=specific_title_fr,
        common_en=common_title_en,
        specific_en=specific_title_en,
    )


def _build_part(
        part_type: str,
        volume_q1: Decimal,
        volume_q2: Decimal,
        volume_annual: Decimal,
        planned_classes: int,
        repartition_entity_1: EntityCode,
        repartition_entity_2: Optional['EntityCode'],
        repartition_entity_3: Optional['EntityCode'],
        repartition_volume_entity_1: Decimal,
        repartition_volume_entity_2: Optional[Decimal],
        repartition_volume_entity_3: Optional[Decimal],
) -> Union['LecturingPart', 'PracticalPart', None]:
    if not volume_annual:
        return
    entity_1 = UclEntityIdentityBuilder.build_from_code(repartition_entity_1)
    entity_2 = UclEntityIdentityBuilder.build_from_code(repartition_entity_2) if repartition_entity_2 else None
    entity_3 = UclEntityIdentityBuilder.build_from_code(repartition_entity_3) if repartition_entity_3 else None
    volumes = Volumes(
        volume_first_quadrimester=volume_q1,
        volume_second_quadrimester=volume_q2,
        volume_annual=volume_annual,
        planned_classes=planned_classes,
        volumes_repartition=FinancialVolumesRepartition(
            responsible_entity=entity_1,
            entity_2=entity_2,
            entity_3=entity_3,
            repartition_volume_responsible_entity=repartition_volume_entity_1,
            repartition_volume_entity_2=repartition_volume_entity_2,
            repartition_volume_entity_3=repartition_volume_entity_3,
        )
    )
    if part_type == LECTURING:
        return LecturingPart(volumes=volumes)
    return PracticalPart(volumes=volumes)


def _build_mobility(english_friendly: bool, french_friendly: bool, exchange_students: bool) -> 'Mobility':
    return Mobility(
        english_friendly=english_friendly,
        french_friendly=french_friendly,
        exchange_students=exchange_students,
    )
