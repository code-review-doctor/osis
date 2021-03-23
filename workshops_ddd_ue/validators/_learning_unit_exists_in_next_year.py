from typing import List

from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import LearningUnitAlreadyExistsException
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity, LearningUnit
from workshops_ddd_ue.factory.learning_unit_identity_factory import LearningUnitIdentityBuilder


class LearningUnitYearExistsNextYearValidator(BusinessValidator):

    def __init__(
            self,
            learning_unit_identity: 'LearningUnitIdentity',
            all_existing_lear_unit_identities: List['LearningUnitIdentity'],
    ):
        super().__init__()
        self.learning_unit_identity = learning_unit_identity
        self.all_existing_learning_units = all_existing_lear_unit_identities
        self.identity_next_year = LearningUnitIdentityBuilder.build_for_next_year(
            learning_unit_identity
        )

    def validate(self, *args, **kwargs):
        if self.identity_next_year in set(self.all_existing_learning_units):
            raise LearningUnitAlreadyExistsException(self.identity_next_year)
