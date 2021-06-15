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

import abc

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from base.models.enums import quadrimesters


class LearningComponentYearQuadriStrategy(metaclass=abc.ABCMeta):
    def __init__(self, lcy):
        self.lcy = lcy

    @abc.abstractmethod
    def is_valid(self):
        raise NotImplementedError


class LearningComponentYearQuadriNoStrategy(LearningComponentYearQuadriStrategy):
    def is_valid(self):
        return True


class LearningComponentYearQ1Strategy(LearningComponentYearQuadriStrategy):
    def is_valid(self):
        if self.lcy.hourly_volume_partial_q2:
            raise ValidationError(_('Only the volume Q1 must have a value'))
        return True


class LearningComponentYearQ2Strategy(LearningComponentYearQuadriStrategy):
    def is_valid(self):
        if self.lcy.hourly_volume_partial_q1:
            raise ValidationError(_('Only the volume Q2 must have a value'))
        return True


class LearningComponentYearQ1and2Strategy(LearningComponentYearQuadriStrategy):
    def is_valid(self):
        if not self.lcy.hourly_volume_partial_q1 or not self.lcy.hourly_volume_partial_q2:
            raise ValidationError(_('The volumes Q1 and Q2 must have a value'))
        return True


class LearningComponentYearQ1or2Strategy(LearningComponentYearQuadriStrategy):
    def is_valid(self):
        if (self.lcy.hourly_volume_partial_q1 and self.lcy.hourly_volume_partial_q2) or\
                (not self.lcy.hourly_volume_partial_q1 and not self.lcy.hourly_volume_partial_q2):
            raise ValidationError(_('The volume Q1 or Q2 must have a value but not both'))
        return True


QUADRIMESTER_CHECK_RULES = {
    quadrimesters.LearningUnitYearQuadrimester.Q1.name: {
        'correct_values': [
            None,
            quadrimesters.LearningUnitYearQuadrimester.Q1.name
        ],
        'available_values_str': 'Q1'
    },
    quadrimesters.LearningUnitYearQuadrimester.Q2.name: {
        'correct_values': [
            None,
            quadrimesters.LearningUnitYearQuadrimester.Q2.name
        ],
        'available_values_str': 'Q2'
    },
    quadrimesters.LearningUnitYearQuadrimester.Q1and2.name: {
        'correct_values': [
            quadrimesters.LearningUnitYearQuadrimester.Q1.name,
            quadrimesters.LearningUnitYearQuadrimester.Q2.name,
            quadrimesters.LearningUnitYearQuadrimester.Q1and2.name,
            quadrimesters.LearningUnitYearQuadrimester.Q1or2.name
        ],
        'available_values_str': 'Q1 {}/{} Q2'.format(_('and'), _('or'))
    },
    quadrimesters.LearningUnitYearQuadrimester.Q1or2.name: {
        'correct_values': [
            quadrimesters.LearningUnitYearQuadrimester.Q1.name,
            quadrimesters.LearningUnitYearQuadrimester.Q2.name,
            quadrimesters.LearningUnitYearQuadrimester.Q1or2.name
        ],
        'available_values_str': 'Q1 {} Q2'.format(_('or'))
    },
    quadrimesters.LearningUnitYearQuadrimester.Q3.name: {
        'correct_values': [
            None,
            quadrimesters.LearningUnitYearQuadrimester.Q3.name,
        ],
        'available_values_str': 'Q3'
    }
}
