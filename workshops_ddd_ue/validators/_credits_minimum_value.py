from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import CreditsShouldBeGreatherThanZeroException

MINIMUM_VALUE = 1


class CreditsMinimumValueValidator(BusinessValidator):

    def __init__(self, credits: int):
        super().__init__()
        self.credits = credits

    def validate(self, *args, **kwargs):
        if self.credits < MINIMUM_VALUE:
            raise CreditsShouldBeGreatherThanZeroException()
