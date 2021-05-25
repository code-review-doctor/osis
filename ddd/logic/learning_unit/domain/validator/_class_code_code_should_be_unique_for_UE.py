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

import attr

from base.ddd.utils.business_validator import BusinessValidator
from ddd.logic.learning_unit.domain.validator.exceptions import CodeClassAlreadyExistForUeException


@attr.s(frozen=True, slots=True)
class ClassCodeShouldBeUniqueForUE(BusinessValidator):
    class_code = attr.ib(type=str)
    learning_unit_id = attr.ib(type='LearningUnitIdentity')  # type: LearningUnitIdentity
    all_existing_class_identities = attr.ib(type=List['EffectiveClassIdentity'])  # type: List['EffectiveClassIdentity']

    def validate(self, *args, **kwargs):
        if self.all_existing_class_identities:
            for id in self.all_existing_class_identities:
                if id.learning_unit_identity == self.learning_unit_id and id.class_code == self.class_code:
                    raise CodeClassAlreadyExistForUeException(self.learning_unit_id, self.class_code)
