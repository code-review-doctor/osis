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

from django.utils.translation import gettext_lazy as _

from osis_common.ddd.interface import BusinessException


class AssignedVolumeInvalidValueException(BusinessException):
    def __init__(self, assigned_volume: float, class_volume: float, **kwargs):
        message = _("Volume of %(assigned_volume)d is not a valid volume. It should be greater or equal than 0 and "
                    "less or equal than the class volume (%(class_volume)d)") % {
            'assigned_volume': assigned_volume,
            'class_volume': class_volume
        }
        super().__init__(message, **kwargs)


class AssignedVolumeTooHighException(BusinessException):
    def __init__(self, assigned_volume: float, attribution_volume: float, **kwargs):
        message = _(
            "Volume of %(assigned_volume)d is not a valid volume. It should be greater or equal than 0 and "
            "less or equal than the attribution volume (%(attribution_volume))") % {
            'assigned_volume': assigned_volume,
            'attribution_volume': attribution_volume
        }
        super().__init__(message, **kwargs)
