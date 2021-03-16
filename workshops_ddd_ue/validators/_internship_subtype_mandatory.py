from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.learning_unit_year import AcademicYear


class InternshipSubtypeMandatoryValidator(BusinessValidator):

    def __init__(self, academic_year: 'AcademicYear'):
        pass

    def validate(self, *args, **kwargs):
        pass
