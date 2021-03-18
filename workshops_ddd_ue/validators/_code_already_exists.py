from typing import List

from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import LearningUnitCodeAlreadyExistsException
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity


class CodeAlreadyExistsValidator(BusinessValidator):

    def __init__(self, code: str, all_existing_identities: List['LearningUnitIdentity']):
        super().__init__()
        self.code = code
        self.all_existing_identities = all_existing_identities

    def validate(self, *args, **kwargs):
        if self.code in {identity.code for identity in self.all_existing_identities}:
            raise LearningUnitCodeAlreadyExistsException(code=self.code)
