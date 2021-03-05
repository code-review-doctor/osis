# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################

from base.ddd.utils import business_validator
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.education_group_types import TrainingType
from education_group.ddd.domain.exception import HopsFieldsAllOrNone, \
    AresCodeShouldBeGreaterOrEqualsThanZeroAndLessThan9999, AresGracaShouldBeGreaterOrEqualsThanZeroAndLessThan9999, \
    AresAuthorizationShouldBeGreaterOrEqualsThanZeroAndLessThan9999, HopsFields2OrNoneForPhd


class HopsValuesValidator(business_validator.BusinessValidator):

    def __init__(self, training: 'Training'):
        super().__init__()

        if training.type in TrainingType.all() and training.hops:
            self.ares_code = training.hops.ares_code
            self.ares_graca = training.hops.ares_graca
            self.ares_authorization = training.hops.ares_authorization
        else:
            self.ares_code = self.ares_graca = self.ares_authorization = None

        self.ares_fields_needed = 3
        self.exception = HopsFieldsAllOrNone()
        if training.type in (TrainingType.PHD, TrainingType.FORMATION_PHD):
            self.ares_fields_needed = 2
            self.exception = HopsFields2OrNoneForPhd()

    def validate(self, *args, **kwargs):
        exceptions = []
        hops_fields_values = [value for value in [self.ares_code, self.ares_graca, self.ares_authorization] if value]

        if 0 < len(hops_fields_values) < self.ares_fields_needed:
            exceptions.append(self.exception)
        else:
            if self.ares_code and not 0 < self.ares_code <= 9999:
                exceptions.append(AresCodeShouldBeGreaterOrEqualsThanZeroAndLessThan9999())

            if self.ares_graca and not 0 < self.ares_graca <= 9999:
                exceptions.append(AresGracaShouldBeGreaterOrEqualsThanZeroAndLessThan9999())

            if self.ares_authorization and not 0 < self.ares_authorization <= 9999:
                exceptions.append(AresAuthorizationShouldBeGreaterOrEqualsThanZeroAndLessThan9999())
        if exceptions:
            raise MultipleBusinessExceptions(exceptions=set(exceptions))
