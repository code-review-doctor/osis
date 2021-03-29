import attr

from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import CreditsShouldBeGreatherThanZeroException, \
    SubdivisionShouldHaveOneLetterException

AUTHORIZED_SUBDIVISION_SIZE = 1


@attr.s(frozen=True, slots=True)
class SubdivisionShouldContainOnlyOneLetterValidator(BusinessValidator):

    subdivision = attr.ib(str)

    def validate(self, *args, **kwargs):
        if len(self.subdivision) != AUTHORIZED_SUBDIVISION_SIZE:
            raise SubdivisionShouldHaveOneLetterException()
