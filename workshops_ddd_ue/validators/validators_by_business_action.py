from typing import List

import attr

from base.ddd.utils.business_validator import MultipleExceptionBusinessListValidator, \
    TwoStepsMultipleBusinessExceptionListValidator, BusinessValidator
from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain.responsible_entity import ResponsibleEntity
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
from workshops_ddd_ue.business_types import *


@attr.s(slots=True)
class CreateLearningUnitValidatorList(TwoStepsMultipleBusinessExceptionListValidator):

    command = attr.ib(type=CreateLearningUnitCommand)
    responsible_entity = attr.ib(type=ResponsibleEntity)
    all_existing_identities = attr.ib(type=List['LearningUnitIdentity'])  # type: List['LearningUnitIdentity']

    def get_data_contract_validators(self) -> List[BusinessValidator]:
        return [
            RequiredFieldsValidator(self.command),
        ]

    def get_invariants_validators(self) -> List[BusinessValidator]:
        return [
            InternshipSubtypeMandatoryValidator(self.command.type, self.command.internship_subtype),
            AcademicYearGreaterThan2019(self.command.academic_year),
            CodeAlreadyExistsValidator(self.command.code, self.all_existing_identities),
            CreditsMinimumValueValidator(self.command.credits),
            CodeStructureValidator(self.command.code),
            ResponsibleEntityAuthorizedTypeOrCode(self.responsible_entity),
        ]


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
