##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from typing import List

from django.utils.translation import gettext_lazy as _

from ddd.logic.learning_unit.business_types import *
from ddd.logic.learning_unit.domain.model._financial_volumes_repartition import DurationUnit
from osis_common.ddd.interface import BusinessException
from program_management.ddd.domain.program_tree import ProgramTreeIdentity


class AcademicYearLowerThan2019Exception(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Can't create a learning unit lower than 2019-20")
        super().__init__(message, **kwargs)


class InvalidResponsibleEntityTypeOrCodeException(BusinessException):
    def __init__(self, entity_code: str, *args, **kwargs):
        message = _(
            "Selected entity {} is not an authorized responsible entity".format(entity_code)
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
    def __init__(
            self,
            learning_unit: 'LearningUnitIdentity',
            program_identities: List['ProgramTreeIdentity'],
            *args,
            **kwargs
    ):
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
        message = _("The subdivision %(subd)s already exists for %(ue)s") % {
            'subd': subdivision,
            'ue': learning_unit_identity,
        }
        super().__init__(message, **kwargs)


class ShouldBeAlphanumericException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _(
            "Subdivision should be one character A-Z or 0-9"
        )
        super().__init__(message, **kwargs)


class CodeClassAlreadyExistForUeException(BusinessException):
    def __init__(self, learning_unit_identity: 'LearningUnitIdentity', code: str, *args, **kwargs):
        message = _("The code %(ue_code)s - %(code)s already exists for %(ue)s") % {
            'ue_code': learning_unit_identity.code,
            'code': code,
            'ue': learning_unit_identity,
        }
        super().__init__(message, **kwargs)


class ClassTypeInvalidException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _(
            "Class can't be neither mobility nor external"
        )
        super().__init__(message, **kwargs)


class LearningUnitHasPartimException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _(
            "Class can't be created on learning unit having partim"
        )
        super().__init__(message, **kwargs)


class LearningUnitHasProposalException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _(
            "You cannot create a class on this learning unit because it is in proposal this year or in past."
        )
        super().__init__(message, **kwargs)


class LearningUnitHasEnrollmentException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _(
            "Class can't be created on learning unit having enrollment"
        )
        super().__init__(message, **kwargs)


class LearningUnitHasNoVolumeException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _(
            "You cannot create class on this learning unit because the component's annual volume [PM or default PP] "
            "is not greater than 0 and there are no planned class."
        )
        super().__init__(message, **kwargs)


class AnnualVolumeInvalidException(BusinessException):
    def __init__(self, volume_annual: 'DurationUnit', *args, **kwargs):
        message = _(
            "The sum of first/second quadrimesters volumes should be equal to annual volume "
            "of the learning unit ({})"
        ).format(volume_annual)
        super().__init__(message, **kwargs)


class DerogationQuadrimesterInvalidChoiceException(BusinessException):
    def __init__(self, derogation_quadrimester: str, **kwargs):
        message = _("'{value}' is not a valid derogation quadrimester.").format(value=derogation_quadrimester)
        super().__init__(message, **kwargs)


class DerogationSessionInvalidChoiceException(BusinessException):
    def __init__(self, derogation_session: str, **kwargs):
        message = _("'{value}' is not a valid derogation session.").format(value=derogation_session)
        super().__init__(message, **kwargs)


class TeachingPlaceRequiredException(BusinessException):
    def __init__(self, **kwargs):
        message = _("The teaching place is required.")
        super().__init__(message, **kwargs)


class EffectiveClassHasTutorAssignedException(BusinessException):
    def __init__(self, effective_class_complete_code: str, tutor_full_name: str, learning_unit_year: int, **kwargs):
        message = _("The class %(class_complete_code)s is assigned to %(tutor_full_name)s in %(year)s") % {
            'class_complete_code': effective_class_complete_code,
            'tutor_full_name': tutor_full_name,
            'year': learning_unit_year,
        }
        super().__init__(message, **kwargs)


class LearningUnitOfEffectiveClassHasEnrollmentException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _(
            "Class of learning unit having enrollment can't be delete"
        )
        super().__init__(message, **kwargs)


class LearningUnitNotExistingException(BusinessException):
    def __init__(self, learning_unit_year: int, **kwargs):
        message = _(
            "You cannot create class in %(year)s because there is no learning unit corresponding in %(year)s"
        ) % {
            'year': learning_unit_year,
        }
        super().__init__(message, **kwargs)
