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

from attribution.models.enums.function import Functions
from ddd.logic.attribution.domain.model._class_volume_repartition import ClassVolumeRepartition
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class LearningUnitAttributionIdentity(interface.EntityIdentity):
    uuid = attr.ib(type=str)


@attr.s(slots=True, hash=False, eq=False)
class LearningUnitAttribution(interface.Entity):
    entity_id = attr.ib(type=LearningUnitAttributionIdentity)
    function = attr.ib(type=Functions)
    learning_unit = attr.ib(type=LearningUnitIdentity)
    distributed_effective_classes = attr.ib(type=List[ClassVolumeRepartition])

    # def manage_distribution(self):
    #     pass
