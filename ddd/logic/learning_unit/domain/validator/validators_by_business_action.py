from typing import List

import attr

from base.ddd.utils.business_validator import TwoStepsMultipleBusinessExceptionListValidator, BusinessValidator
from ddd.logic.learning_unit.commands import CreateLearningUnitCommand, CreateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model._volumes_repartition import Volumes, Duration
from ddd.logic.learning_unit.domain.validator._check_class_volumes import CheckClassVolumes
from ddd.logic.learning_unit.domain.validator._should_academic_year_be_greater_than_2019 import \
    ShouldAcademicYearGreaterThan2019
from ddd.logic.learning_unit.domain.validator._should_code_not_exist import ShouldCodeAlreadyExistsValidator
from ddd.logic.learning_unit.domain.validator._should_credits_respect_minimum_value import \
    ShouldCreditsRespectMinimumValueValidator
from ddd.logic.learning_unit.domain.validator._should_fields_be_required import ShouldFieldsBeRequiredValidator
from ddd.logic.learning_unit.domain.validator._should_internship_subtype_be_mandatory import \
    ShouldInternshipSubtypeBeMandatoryValidator
from ddd.logic.learning_unit.domain.validator._should_learning_unit_code_respect_naming_convention import \
    ShouldCodeRespectNamingConventionValidator
from ddd.logic.learning_unit.domain.validator._should_learning_unit_not_exists_in_next_year import \
    ShouldLearningUnitNotExistNextYearValidator
from ddd.logic.learning_unit.domain.validator._should_not_be_type_mobility_or_external import \
    ShouldNotBeTypeMobilityOrExternal
from ddd.logic.learning_unit.domain.validator._subdivision_code_should_be_unique_for_UE import \
    SubdivisionCodeShouldBeUniqueForUE
from ddd.logic.learning_unit.domain.validator._subdivision_should_contain_only_one_letter import \
    SubdivisionShouldContainOnlyOneLetterValidator
from ddd.logic.learning_unit.domain.validator._subdivision_should_not_exist import SubdivisionShouldNotExistValidator
from ddd.logic.learning_unit.domain.validator.exceptions import ShouldBeAlphanumericException


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


@attr.s(frozen=True, slots=True)
class CreateEffectiveClassValidatorList(TwoStepsMultipleBusinessExceptionListValidator):

    command = attr.ib(type=CreateEffectiveClassCommand)
    learning_unit = attr.ib(type='LearningUnit')
    all_existing_class_identities = attr.ib(type=List['EffectiveClassIdentity'])

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return [
            ShouldBeAlphanumericException(self.command.class_code)
        ]

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            SubdivisionCodeShouldBeUniqueForUE(
                self.command.learning_unit_code,
                self.learning_unit.entity_id,
                self.all_existing_class_identities
            ),
            ShouldNotBeTypeMobilityOrExternal(self.learning_unit),
            CheckClassVolumes(
                Volumes(
                    volume_first_quadrimester=Duration(
                        hours=self.command.volume_first_quadrimester_hours,
                        minutes=self.command.volume_first_quadrimester_minutes
                    ),
                    volume_second_quadrimester=Duration(
                        hours=self.command.volume_second_quadrimester_hours,
                        minutes=self.command.volume_second_quadrimester_minutes
                    ),
                    volume_annual=Duration(
                        hours=self.command.volume_annual_quadrimester_hours,
                        minutes=self.command.volume_annual_quadrimester_minutes
                    )
                )
            )
        ]
