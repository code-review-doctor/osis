from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import AcademicYearLowerThan2019Exception

LIMIT_YEAR_TO_CREATE_LEARNING_UNIT = 2019


class AcademicYearGreaterThan2019(BusinessValidator):

    def __init__(self, year: int):
        super().__init__()
        self.year = year

    def validate(self, *args, **kwargs):
        if self.year < LIMIT_YEAR_TO_CREATE_LEARNING_UNIT:
            raise AcademicYearLowerThan2019Exception()
