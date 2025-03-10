##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.models.utils.utils import ChoiceEnum


SESSION_P23 = "P23"
SESSION_XX3 = "3"
SESSION_X2X = "2"
SESSION_X23 = "23"
SESSION_1XX = "1"
SESSION_1X3 = "13"
SESSION_12X = "12"
SESSION_123 = "123"

LEARNING_UNIT_YEAR_SESSION = ((SESSION_1XX, SESSION_1XX),
                              (SESSION_X2X, SESSION_X2X),
                              (SESSION_XX3, SESSION_XX3),
                              (SESSION_12X, SESSION_12X),
                              (SESSION_1X3, SESSION_1X3),
                              (SESSION_X23, SESSION_X23),
                              (SESSION_123, SESSION_123),
                              (SESSION_P23, SESSION_P23))


# TODO :: move this into ddd/domain layer
class DerogationSession(ChoiceEnum):
    DEROGATION_SESSION_1XX = _("1")
    DEROGATION_SESSION_X2X = _("2")
    DEROGATION_SESSION_XX3 = _("3")
    DEROGATION_SESSION_12X = _("12")
    DEROGATION_SESSION_1X3 = _("13")
    DEROGATION_SESSION_X23 = _("23")
    DEROGATION_SESSION_123 = _("123")
    DEROGATION_SESSION_P23 = _("P23")
