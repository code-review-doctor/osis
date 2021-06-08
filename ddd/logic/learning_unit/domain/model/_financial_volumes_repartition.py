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

from ddd.logic.learning_unit.domain.model.responsible_entity import UCLEntityIdentity
from osis_common.ddd import interface

DurationUnit = Decimal


@attr.s(frozen=True, slots=True)
class FinancialVolumesRepartition(interface.ValueObject):
    responsible_entity = attr.ib(type=UCLEntityIdentity)
    entity_2 = attr.ib(type=UCLEntityIdentity)
    entity_3 = attr.ib(type=UCLEntityIdentity)
    repartition_volume_responsible_entity = attr.ib(type=DurationUnit)
    repartition_volume_entity_2 = attr.ib(type=DurationUnit)
    repartition_volume_entity_3 = attr.ib(type=DurationUnit)
