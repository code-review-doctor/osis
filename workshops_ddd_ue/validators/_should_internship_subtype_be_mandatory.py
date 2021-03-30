import attr

from base.ddd.utils.business_validator import BusinessValidator
from base.models.enums.learning_container_year_types import LearningContainerYearType
from workshops_ddd_ue.domain.exceptions import InternshipSubtypeMandatoryException


@attr.s(frozen=True, slots=True)
class ShouldInternshipSubtypeBeMandatoryValidator(BusinessValidator):

    learning_unit_type = attr.ib(type=str)
    internship_subtype = attr.ib(type=str)

    def validate(self, *args, **kwargs):
        if self.learning_unit_type == LearningContainerYearType.INTERNSHIP.name and not self.internship_subtype:
            raise InternshipSubtypeMandatoryException()
