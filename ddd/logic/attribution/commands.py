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

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class SearchAttributionsToLearningUnitCommand(interface.CommandRequest):
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)
    class_type = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class SearchTutorsDistributedToClassCommand(interface.CommandRequest):
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)
    class_code = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class DistributeClassToTutorCommand(interface.CommandRequest):
    tutor_personal_id_number = attr.ib(type=str)
    learning_unit_attribution_uuid = attr.ib(type=str)
    class_code = attr.ib(type=str)
    distributed_volume = attr.ib(type=Decimal)
    learning_unit_code = attr.ib(type=str)
    year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class CheckTutorAlreadyDistributedToClassCommand(interface.CommandRequest):
    tutor_personal_id_number = attr.ib(type=str)
    learning_unit_attribution_uuid = attr.ib(type=str)
    class_code = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class UnassignTutorClassCommand(interface.CommandRequest):
    tutor_personal_id_number = attr.ib(type=str)
    learning_unit_attribution_uuid = attr.ib(type=str)
    class_code = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class SearchAttributionCommand(interface.CommandRequest):
    learning_unit_attribution_uuid = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)
