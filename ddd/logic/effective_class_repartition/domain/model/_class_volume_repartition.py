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
from decimal import Decimal

import attr

from ddd.logic.effective_class_repartition.domain.model._learning_unit_attribution import \
    LearningUnitAttributionIdentity
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from osis_common.ddd import interface


@attr.s(slots=True, hash=False, eq=False)
class ClassVolumeRepartition(interface.ValueObject):
    effective_class = attr.ib(type=EffectiveClassIdentity)
    distributed_volume = attr.ib(type=Decimal)
    attribution = attr.ib(type=LearningUnitAttributionIdentity)

    def __hash__(self):
        return hash("{}{}".format(self.effective_class, self.attribution))

    def __eq__(self, other):
        return hash(self) == hash(other)
