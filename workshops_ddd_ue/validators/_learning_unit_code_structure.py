import re

from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import LearningUnitCodeStructureInvalidException

LEARNING_UNIT_ACRONYM_REGEX_BASE = "^[BELMWX][A-Z]{2,4}[1-9]\d{3}"
STRING_END = "$"
LEARNING_UNIT_ACRONYM_REGEX_FULL = LEARNING_UNIT_ACRONYM_REGEX_BASE + STRING_END


class CodeStructureValidator(BusinessValidator):

    def __init__(self, code: str):
        super().__init__()
        self.code = code

    def validate(self, *args, **kwargs):
        if not bool(re.match(LEARNING_UNIT_ACRONYM_REGEX_FULL, self.code)):
            raise LearningUnitCodeStructureInvalidException(code=self.code)
