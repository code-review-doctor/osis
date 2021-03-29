from typing import List

import attr

from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import LearningUnitAlreadyExistsException
from workshops_ddd_ue.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from workshops_ddd_ue.business_types import *


@attr.s(frozen=True, slots=True)
class LearningUnitYearExistsNextYearValidator(BusinessValidator):
    learning_unit_identity = attr.ib(type='LearningUnitIdentity')  # type: LearningUnitIdentity
    all_existing_lear_unit_identities = attr.ib(type=List['LearningUnitIdentity'])  # type: List[LearningUnitIdentity]

    def validate(self, *args, **kwargs):
        identity_next_year = LearningUnitIdentityBuilder.build_for_next_year(
            self.learning_unit_identity
        )
        if identity_next_year in set(self.all_existing_lear_unit_identities):
            raise LearningUnitAlreadyExistsException(identity_next_year)
