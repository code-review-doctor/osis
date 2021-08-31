#set( $Validator = ${StringUtils.removeAndHump($NAME)} )
from typing import Optional

import attr

from base.ddd.utils.business_validator import BusinessValidator


@attr.s(frozen=True, slots=True)
class ${$Validator}(BusinessValidator):
    attr = attr.ib(type=str)

    def validate(self, *args, **kwargs):
        raise BusinessException()