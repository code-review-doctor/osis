from typing import List

import attr

from base.ddd.utils.business_validator import TwoStepsMultipleBusinessExceptionListValidator, BusinessValidator
from workshops_ddd_ue.business_types import *
from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain.responsible_entity import ResponsibleEntity
from workshops_ddd_ue.validators._should_academic_year_be_greater_than_2019 import ShouldAcademicYearGreaterThan2019
from workshops_ddd_ue.validators._should_code_not_exist import ShouldCodeAlreadyExistsValidator
from workshops_ddd_ue.validators._should_credits_respect_minimum_value import ShouldCreditsRespectMinimumValueValidator
from workshops_ddd_ue.validators._should_fields_be_required import ShouldFieldsBeRequiredValidator
from workshops_ddd_ue.validators._should_internship_subtype_be_mandatory import \
    ShouldInternshipSubtypeBeMandatoryValidator
from workshops_ddd_ue.validators._should_learning_unit_code_respect_naming_convention import \
    ShouldCodeRespectNamingConventionValidator
from workshops_ddd_ue.validators._should_learning_unit_not_exists_in_next_year import \
    ShouldLearningUnitNotExistNextYearValidator
from workshops_ddd_ue.validators._should_responsible_entity_have_authorized_type_or_code import \
    ShouldResponsibleEntityHaveAuthorizedTypeOrCode
from workshops_ddd_ue.validators._subdivision_should_contain_only_one_letter import \
    SubdivisionShouldContainOnlyOneLetterValidator
from workshops_ddd_ue.validators._subdivision_should_not_exist import SubdivisionShouldNotExistValidator


@attr.s(frozen=True, slots=True)
class CreateLearningUnitValidatorList(TwoStepsMultipleBusinessExceptionListValidator):

    command = attr.ib(type=CreateLearningUnitCommand)
    all_existing_identities = attr.ib(type=List['LearningUnitIdentity'])  # type: List[LearningUnitIdentity]

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return [
            ShouldFieldsBeRequiredValidator(self.command),
        ]

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldInternshipSubtypeBeMandatoryValidator(self.command.type, self.command.internship_subtype),
            ShouldAcademicYearGreaterThan2019(self.command.academic_year),
            ShouldCodeAlreadyExistsValidator(self.command.code, self.all_existing_identities),
            ShouldCreditsRespectMinimumValueValidator(self.command.credits),
            ShouldCodeRespectNamingConventionValidator(self.command.code),
        ]


@attr.s(frozen=True, slots=True)
class CopyLearningUnitToNextYearValidatorList(TwoStepsMultipleBusinessExceptionListValidator):

    learning_unit_identity = attr.ib(type='LearningUnitIdentity')  # type: LearningUnitIdentity
    all_existing_lear_unit_identities = attr.ib(type=List['LearningUnitIdentity'])  # type: List[LearningUnitIdentity]

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            ShouldLearningUnitNotExistNextYearValidator(
                self.learning_unit_identity,
                self.all_existing_lear_unit_identities
            ),
        ]


@attr.s(frozen=True, slots=True)
class CreatePartimValidatorList(TwoStepsMultipleBusinessExceptionListValidator):

    learning_unit = attr.ib(type='LearningUnit')  # type: LearningUnit
    subdivision = attr.ib(type=str)

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return []

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            SubdivisionShouldContainOnlyOneLetterValidator(self.subdivision),
            SubdivisionShouldNotExistValidator(self.subdivision, self.learning_unit),
        ]
