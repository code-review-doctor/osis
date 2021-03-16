from base.ddd.utils.business_validator import MultipleExceptionBusinessListValidator
from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain.learning_unit_year import ResponsibleEntity
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository
from workshops_ddd_ue.validators._academic_year_greater_than_2019 import AcademicYearGreaterThan2019
from workshops_ddd_ue.validators._code_already_exists import CodeAlreadyExistsValidator
from workshops_ddd_ue.validators._credits_minimum_value import CreditsMinimumValueValidator
from workshops_ddd_ue.validators._learning_unit_code_structure import CodeStructureValidator
from workshops_ddd_ue.validators._required_fields import RequiredFieldsValidator
from workshops_ddd_ue.validators._responsible_entity_authorized_type_or_code import \
    ResponsibleEntityAuthorizedTypeOrCode


class CreateLearningUnitValidatorList(MultipleExceptionBusinessListValidator):
    def __init__(
            self,
            repository: LearningUnitRepository,
            responsible_entity: 'ResponsibleEntity',
            command: CreateLearningUnitCommand,
    ):
        self.validators = [
            AcademicYearGreaterThan2019(command.academic_year),
            CodeAlreadyExistsValidator(command.code, repository),
            CreditsMinimumValueValidator(command.credits),
            CodeStructureValidator(command.code),
            RequiredFieldsValidator(command),
            ResponsibleEntityAuthorizedTypeOrCode(responsible_entity),
        ]
        super().__init__()
