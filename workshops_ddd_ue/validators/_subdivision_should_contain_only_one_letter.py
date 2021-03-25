from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import CreditsShouldBeGreatherThanZeroException, \
    SubdivisionShouldHaveOneLetterException

AUTHORIZED_SUBDIVISION_SIZE = 1


class SubdivisionShouldContainOnlyOneLetterValidator(BusinessValidator):

    def __init__(self, subdivision: str):
        super().__init__()
        self.subdivision = subdivision

    def validate(self, *args, **kwargs):
        if len(self.subdivision) != AUTHORIZED_SUBDIVISION_SIZE:
            raise SubdivisionShouldHaveOneLetterException()
