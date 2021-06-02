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

from base.models.enums import learning_unit_year_session

CORRECT_VALUES_23 = [
    None,
    learning_unit_year_session.SESSION_X2X,
    learning_unit_year_session.SESSION_XX3,
    learning_unit_year_session.SESSION_X23,
    learning_unit_year_session.SESSION_P23
]

AVAILABLE_VALUES_STR_23 = "2, 3, 23 {} P23".format(_('or'))

SESSION_CHECK_RULES = {
    learning_unit_year_session.SESSION_1XX: {
        'correct_values': [
            None,
            learning_unit_year_session.SESSION_1XX
        ],
        'available_values_str': '1'
    },
    learning_unit_year_session.SESSION_X2X: {
        'correct_values': [
            None,
            learning_unit_year_session.SESSION_X2X
        ],
        'available_values_str': '2'
    },
    learning_unit_year_session.SESSION_XX3: {
        'correct_values': [
            None,
            learning_unit_year_session.SESSION_XX3
        ],
        'available_values_str': '3'
    },

    learning_unit_year_session.SESSION_12X: {
        'correct_values': [
            None,
            learning_unit_year_session.SESSION_1XX,
            learning_unit_year_session.SESSION_X2X,
            learning_unit_year_session.SESSION_12X
        ],
        'available_values_str': '1, 2 {} 12'.format(_('or'))
    },
    learning_unit_year_session.SESSION_1X3: {
        'correct_values': [
            None,
            learning_unit_year_session.SESSION_1XX,
            learning_unit_year_session.SESSION_XX3,
            learning_unit_year_session.SESSION_1X3
        ],
        'available_values_str': '1, 3 {} 13'.format(_('or'))
    },
    learning_unit_year_session.SESSION_X23: {
        'correct_values': CORRECT_VALUES_23,
        'available_values_str': AVAILABLE_VALUES_STR_23
    },
    learning_unit_year_session.SESSION_P23: {
        'correct_values': CORRECT_VALUES_23,
        'available_values_str': AVAILABLE_VALUES_STR_23
    },
}
