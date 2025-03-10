# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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

import re

from base.ddd.utils import business_validator
from base.models.enums.education_group_types import GroupType
from program_management.ddd.domain.exception import CodePatternException

CODE_REGEX = "^([LWMBlwmb])([A-Z0-9]+)$"


class CodePatternValidator(business_validator.BusinessValidator):
    def __init__(self, code: str, training_type: str):
        super().__init__()
        self.code = code
        self.training_type = training_type

    def validate(self, *args, **kwargs):
        if self.code and self.training_type != GroupType.SUB_GROUP.name and \
                not bool(re.match(CODE_REGEX, self.code.upper())):
            raise CodePatternException(self.code.upper())
