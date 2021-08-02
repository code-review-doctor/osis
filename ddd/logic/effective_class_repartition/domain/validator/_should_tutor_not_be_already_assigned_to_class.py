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
from ddd.logic.effective_class_repartition.domain.validator.exceptions import TutorAlreadyAssignedException


@attr.s(frozen=True, slots=True)
class ShouldTutorNotBeAlreadyAssignedToClass(BusinessValidator):
    attribution_uuid = attr.ib(type=str)
    tutor = attr.ib(type='Tutor')  # type: Tutor
    class_code = attr.ib(type='EffectiveClassCode')

    def validate(self, *args, **kwargs):
        attribution_uuids_already_distributed = [
            (distributed_class.attribution_uuid, distributed_class.class_code)
            for distributed_class in self.tutor.distributed_effective_classes
        ]
        if (self.attribution_uuid, self.class_code) in attribution_uuids_already_distributed:
            raise TutorAlreadyAssignedException()
