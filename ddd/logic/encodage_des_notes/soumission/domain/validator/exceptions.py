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


class EnseignantNonAttribueUniteEnseignementException(BusinessException):
    def __init__(self, code_unite_enseignement: str, **kwargs):
        message = _("You're not attributed to the learning unit {}").format(code_unite_enseignement)
        super().__init__(message, **kwargs)


class PeriodeSoumissionNotesFermeeException(BusinessException):
    def __init__(self, **kwargs):
        message = _("The period of scores' encoding is not opened")
        super().__init__(message, **kwargs)


class DateRemiseNoteAtteinteException(BusinessException):
    def __init__(self, **kwargs):
        message = _("Deadline reached")
        super().__init__(message, **kwargs)


class AucunEtudiantTrouveException(BusinessException):
    def __init__(self, learning_unit_code: str, email: str, **kwargs):
        message = _("No exam enrollment found for {learning_unit_code} (student = {email}").format(
            learning_unit_code=learning_unit_code,
            email=email,
        )
        super().__init__(message, **kwargs)
