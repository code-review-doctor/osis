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
from osis_common.ddd.interface import BusinessException

from django.utils.translation import gettext_lazy as _


class EmptyRequiredFieldException(BusinessException):
    def __init__(self, empty_required_field: str, *args, **kwargs):
        message = _("Following field is required : {}").format(empty_required_field)
        super().__init__(message, **kwargs)


class LecturingAndPracticalNotFilledException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Lecturing charge or practical charge must be filled")
        super().__init__(message, **kwargs)


class ApplicationAlreadyExistsException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("You have already applied on vacant course")
        super().__init__(message, **kwargs)


class VacantCourseApplicationManagedInTeamException(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("This course is team-managed. The application to this activity is based on a paper transmission.")
        super().__init__(message, **kwargs)


class VolumesAskedShouldBeLowerOrEqualToVolumeAvailable(BusinessException):
    def __init__(self, *args, **kwargs):
        message = _("Volumes asked should be lower or equal to volume available")
        super().__init__(message, **kwargs)


class AttributionAboutToExpireNotFound(BusinessException):
    def __init__(self, *args, code: str, **kwargs):
        message = _("Cannot found attribution about to expire with code: {}".format(code))
        super().__init__(message, **kwargs)


class AttributionAboutToExpireFunctionException(BusinessException):
    def __init__(self, *args,  **kwargs):
        message = _("Cannot renew an attribution with a function different from holder or coholder")
        super().__init__(message, **kwargs)
