from typing import List

import attr

from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import LearningUnitCodeAlreadyExistsException
from workshops_ddd_ue.business_types import *


@attr.s(frozen=True, slots=True)
class ShouldCodeAlreadyExistsValidator(BusinessValidator):

    code = attr.ib(type=str)
    all_existing_identities = attr.ib(type=List['LearningUnitIdentity'])  # type: List[LearningUnitIdentity]

    def validate(self, *args, **kwargs):
        if self.code in {identity.code for identity in self.all_existing_identities}:
            raise LearningUnitCodeAlreadyExistsException(code=self.code)
