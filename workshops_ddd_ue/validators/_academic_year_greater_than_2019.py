from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import AcademicYearLowerThan2019Exception
from workshops_ddd_ue.domain.learning_unit_year import AcademicYear


LIMIT_YEAR_TO_CREATE_LEARNING_UNIT = 2019


class AcademicYearGreaterThan2019(BusinessValidator):

    def __init__(self, academic_year: 'AcademicYear'):
        super().__init__()
        self.academic_year = academic_year

    def validate(self, *args, **kwargs):
        if self.academic_year.year < LIMIT_YEAR_TO_CREATE_LEARNING_UNIT:
            raise AcademicYearLowerThan2019Exception()
