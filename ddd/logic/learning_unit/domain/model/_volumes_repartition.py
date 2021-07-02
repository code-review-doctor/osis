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

from ddd.logic.learning_unit.domain.model._financial_volumes_repartition import FinancialVolumesRepartition, \
    DurationUnit
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class ClassVolumes(interface.ValueObject):
    volume_first_quadrimester = attr.ib(type=DurationUnit)
    volume_second_quadrimester = attr.ib(type=DurationUnit)

    @property
    def total_volume(self) -> DurationUnit:
        return (self.volume_first_quadrimester or 0) + (self.volume_second_quadrimester or 0)


@attr.s(frozen=True, slots=True)
class Volumes(interface.ValueObject):
    volume_annual = attr.ib(type=DurationUnit)
    planned_classes = attr.ib(type=int)
    volumes_repartition = attr.ib(type=FinancialVolumesRepartition)
    volume_first_quadrimester = attr.ib(type=DurationUnit, default=0.0)
    volume_second_quadrimester = attr.ib(type=DurationUnit, default=0.0)


@attr.s(frozen=True, slots=True)
class LecturingPart(interface.ValueObject):
    acronym = 'PM'
    volumes = attr.ib(type=Volumes)


@attr.s(frozen=True, slots=True)
class PracticalPart(interface.ValueObject):
    acronym = 'PP'
    volumes = attr.ib(type=Volumes)
