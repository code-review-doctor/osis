from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import LearningUnitCodeAlreadyExistsException
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository


class CodeAlreadyExistsValidator(BusinessValidator):

    def __init__(self, code: str, repository: 'LearningUnitRepository'):
        super().__init__()
        self.code = code
        self.repository = repository

    def validate(self, *args, **kwargs):
        if self.repository.search(code=self.code):
            raise LearningUnitCodeAlreadyExistsException(code=self.code)
