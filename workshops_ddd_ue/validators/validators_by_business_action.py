from base.ddd.utils.business_validator import MultipleExceptionBusinessListValidator
from workshops_ddd_ue.domain.learning_unit_year import AcademicYear, ResponsibleEntity
from workshops_ddd_ue.validators._academic_year_greater_than_2019 import AcademicYearGreaterThan2019
from workshops_ddd_ue.validators._responsible_entity_authorized_type_or_code import \
    ResponsibleEntityAuthorizedTypeOrCode


class CreateLearningUnitValidatorList(MultipleExceptionBusinessListValidator):
    def __init__(self, academic_year: AcademicYear, responsible_entity: 'ResponsibleEntity'):
        self.validators = [
            AcademicYearGreaterThan2019(academic_year),
            ResponsibleEntityAuthorizedTypeOrCode(responsible_entity),
        ]
        super().__init__()
