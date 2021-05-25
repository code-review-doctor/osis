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
import attr

from base.ddd.utils.business_validator import BusinessValidator
from ddd.logic.learning_unit.domain.validator.exceptions import AnnualVolumeInvalidException


@attr.s(frozen=True, slots=True)
class CheckClassVolumeAnnualConsistency(BusinessValidator):

    volume_first_quadrimester = attr.ib(type=float)
    volume_second_quadrimester = attr.ib(type=float)
    volume_annual = attr.ib(type=float)

    def validate(self, *args, **kwargs):
        sum_q1_q2 = self.volume_first_quadrimester + self.volume_second_quadrimester

        if self.volume_annual <= 0 or sum_q1_q2 != self.volume_annual:
            raise AnnualVolumeInvalidException()
