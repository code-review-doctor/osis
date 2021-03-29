from typing import List

from base.models.enums.entity_type import EntityType
from osis_common.ddd.interface import BusinessException
from django.utils.translation import gettext_lazy as _

from program_management.ddd.domain.program_tree import ProgramTreeIdentity
from workshops_ddd_ue.business_types import *


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


class LearningUnitCodeAlreadyExistsException(BusinessException):
    def __init__(self, code: str, *args, **kwargs):
        message = _(
            "The code {} already exists"
        ).format(code)
        super().__init__(message, **kwargs)


class LearningUnitCodeStructureInvalidException(BusinessException):
    def __init__(self, code: str, *args, **kwargs):
        message = _("The code {} is not a valid code").format(code)
        super().__init__(message, **kwargs)


class EmptyRequiredFieldsException(BusinessException):
    def __init__(self, empty_required_fields: List[str], *args, **kwargs):
        message = _("Following fields are required : {}").format(empty_required_fields)
        super().__init__(message, **kwargs)


class LearningUnitUsedInProgramTreeException(BusinessException):
    def __init__(self, learning_unit: 'LearningUnitIdentity', program_identities: List['ProgramTreeIdentity'], *args, **kwargs):
        message = _("Learning unit {} is used in following programs : {}").format(
            learning_unit,
            ",".join([identity.code for identity in program_identities])
        )
        super().__init__(message, **kwargs)


class InternshipSubtypeMandatoryException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Internship subtype is a mandatory field")
        super().__init__(message, **kwargs)


class LearningUnitAlreadyExistsException(BusinessException):
    def __init__(self, learning_unit_identity: 'LearningUnitIdentity', *args, **kwargs):
        message = _("Learning unit {} already exists next year").format(learning_unit_identity)
        super().__init__(message, **kwargs)


class SubdivisionShouldHaveOneLetterException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("The subdivision must contain only one letter")
        super().__init__(message, **kwargs)


class SubdivisionAlreadyExistException(BusinessException):
    def __init__(self, learning_unit_identity: 'LearningUnitIdentity', subdivision: str, *args, **kwargs):
        message = _("The subdivision {subd} already exists for {ue}").format(
            subd=subdivision,
            ue=learning_unit_identity,
        )
        super().__init__(message, **kwargs)
