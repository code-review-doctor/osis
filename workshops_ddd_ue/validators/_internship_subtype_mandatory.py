from base.ddd.utils.business_validator import BusinessValidator
from base.models.enums.internship_subtypes import InternshipSubtype
from base.models.enums.learning_container_year_types import LearningContainerYearType
from workshops_ddd_ue.domain.exceptions import InternshipSubtypeMandatoryException


class InternshipSubtypeMandatoryValidator(BusinessValidator):

    def __init__(self, learning_unit_type: 'LearningContainerYearType', internship_subtype: 'InternshipSubtype'):
        super().__init__()
        self.learning_unit_type = learning_unit_type
        self.internship_subtype = internship_subtype

    def validate(self, *args, **kwargs):
        if self.learning_unit_type == LearningContainerYearType.INTERNSHIP and not self.internship_subtype:
            raise InternshipSubtypeMandatoryException()
