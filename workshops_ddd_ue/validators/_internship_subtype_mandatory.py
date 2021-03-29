import attr

from base.ddd.utils.business_validator import BusinessValidator
from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from workshops_ddd_ue.domain.exceptions import InternshipSubtypeMandatoryException


@attr.s(frozen=True, slots=True)
class InternshipSubtypeMandatoryValidator(BusinessValidator):

    learning_unit_type = attr.ib(type=LearningContainerYearType)
    internship_subtype = attr.ib(type=InternshipSubtype)

    def validate(self, *args, **kwargs):
        if self.learning_unit_type == LearningContainerYearType.INTERNSHIP and not self.internship_subtype:
            raise InternshipSubtypeMandatoryException()
