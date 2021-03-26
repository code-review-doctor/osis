from typing import List

from base.ddd.utils.business_validator import MultipleExceptionBusinessListValidator
from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain.responsible_entity import ResponsibleEntity
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity, LearningUnit
from workshops_ddd_ue.dto.learning_unit_dto import LearningUnitDataDTO
from workshops_ddd_ue.validators._academic_year_greater_than_2019 import AcademicYearGreaterThan2019
from workshops_ddd_ue.validators._code_already_exists import CodeAlreadyExistsValidator
from workshops_ddd_ue.validators._credits_minimum_value import CreditsMinimumValueValidator
from workshops_ddd_ue.validators._internship_subtype_mandatory import InternshipSubtypeMandatoryValidator
from workshops_ddd_ue.validators._learning_unit_code_structure import CodeStructureValidator
from workshops_ddd_ue.validators._learning_unit_exists_in_next_year import LearningUnitYearExistsNextYearValidator
from workshops_ddd_ue.validators._required_fields import RequiredFieldsValidator
from workshops_ddd_ue.validators._responsible_entity_authorized_type_or_code import \
    ResponsibleEntityAuthorizedTypeOrCode
from workshops_ddd_ue.validators._subdivision_should_contain_only_one_letter import \
    SubdivisionShouldContainOnlyOneLetterValidator
from workshops_ddd_ue.validators._subdivision_should_not_exist import SubdivisionShouldNotExistValidator


class CreateLearningUnitValidatorList(MultipleExceptionBusinessListValidator):
    def __init__(
            self,
            dto: 'LearningUnitDataDTO',
            all_existing_identities: List['LearningUnitIdentity']
    ):
        self.validators = [
            AcademicYearGreaterThan2019(dto.year),
            CodeAlreadyExistsValidator(dto.code, all_existing_identities),
            CreditsMinimumValueValidator(dto.credits),
            CodeStructureValidator(dto.code),
            RequiredFieldsValidator(dto),
            ResponsibleEntityAuthorizedTypeOrCode(dto.responsible_entity_code, dto.responsible_entity_type),
            InternshipSubtypeMandatoryValidator(dto.type, dto.internship_subtype),
        ]
        super().__init__()


class CopyLearningUnitToNextYearValidatorList(MultipleExceptionBusinessListValidator):
    def __init__(
            self,
            learning_unit_identity: 'LearningUnitIdentity',
            all_existing_lear_unit_identities: List['LearningUnitIdentity'],
    ):
        self.validators = [
            LearningUnitYearExistsNextYearValidator(learning_unit_identity, all_existing_lear_unit_identities),
        ]
        super().__init__()


class CreatePartimValidatorList(MultipleExceptionBusinessListValidator):
    def __init__(
            self,
            learning_unit: 'LearningUnit',
            subdivision: str,
    ):
        self.validators = [
            SubdivisionShouldContainOnlyOneLetterValidator(subdivision),
            SubdivisionShouldNotExistValidator(subdivision, learning_unit),
        ]
        super().__init__()
