from typing import List

from base.models.enums.entity_type import EntityType
from osis_common.ddd.interface import BusinessException
from django.utils.translation import gettext_lazy as _


class AcademicYearLowerThan2019Exception(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Can't create a learning unit lower than 2019-20")
        super().__init__(message, **kwargs)


class InvalidResponsibleEntityTypeOrCodeException(BusinessException):
    def __init__(self, authorized_types: List['EntityType'], authorized_codes: List['str'],  *args, **kwargs):
        message = _(
            "Responsible entity must be of types = {authorized_types} or haing code = {authorized_codes}".format(
                authorized_types=authorized_types,
                authorized_codes=authorized_codes,
            )
        )
        super().__init__(message, **kwargs)


class CreditsShouldBeGreatherThanZeroException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _(
            "Credits should be greather than 0"
        )
        super().__init__(message, **kwargs)
