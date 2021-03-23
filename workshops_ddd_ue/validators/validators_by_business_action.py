from typing import List

from base.ddd.utils.business_validator import MultipleExceptionBusinessListValidator
from program_management.ddd.domain.program_tree import ProgramTree
from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain._responsible_entity import ResponsibleEntity
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository
from workshops_ddd_ue.validators._academic_year_greater_than_2019 import AcademicYearGreaterThan2019
from workshops_ddd_ue.validators._code_already_exists import CodeAlreadyExistsValidator
from workshops_ddd_ue.validators._credits_minimum_value import CreditsMinimumValueValidator
from workshops_ddd_ue.validators._learning_unit_code_structure import CodeStructureValidator
from workshops_ddd_ue.validators._required_fields import RequiredFieldsValidator
from workshops_ddd_ue.validators._responsible_entity_authorized_type_or_code import \
    ResponsibleEntityAuthorizedTypeOrCode
from workshops_ddd_ue.validators._used_in_program_tree import UsedInProgramValidator


class CreateLearningUnitValidatorList(MultipleExceptionBusinessListValidator):
    def __init__(
            self,
            responsible_entity: 'ResponsibleEntity',
            command: CreateLearningUnitCommand,
            all_existing_identities: List['LearningUnitIdentity']
    ):
        self.validators = [
            AcademicYearGreaterThan2019(command.academic_year),
            CodeAlreadyExistsValidator(command.code, all_existing_identities),
            CreditsMinimumValueValidator(command.credits),
            CodeStructureValidator(command.code),
            RequiredFieldsValidator(command),
            ResponsibleEntityAuthorizedTypeOrCode(responsible_entity),
        ]
        super().__init__()
