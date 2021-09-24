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
import datetime
from decimal import Decimal
from typing import List

import attr

from attribution.models.enums.function import Functions
from osis_common.ddd.interface import DTO


@attr.s(frozen=True, slots=True)
class AcademicYearDataDTO(DTO):
    year = attr.ib(type=str)
    start_date = attr.ib(type=datetime.date)
    end_date = attr.ib(type=datetime.date)


@attr.s(frozen=True, slots=True)
class DistributedEffectiveClassesDTO(DTO):
    class_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)
    distributed_volume = attr.ib(type=Decimal)
    attribution_uuid = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class TutorSearchDTO(DTO):
    personal_id_number = attr.ib(type=str)
    distributed_classes = attr.ib(type=List[DistributedEffectiveClassesDTO])


@attr.s(frozen=True, slots=True)
class TutorAttributionToLearningUnitDTO(DTO):
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=str)
    attribution_uuid = attr.ib(type=str)
    last_name = attr.ib(type=str)
    first_name = attr.ib(type=str)
    personal_id_number = attr.ib(type=str)
    function = attr.ib(type=str)
    lecturing_volume_attributed = attr.ib(type=Decimal)
    practical_volume_attributed = attr.ib(type=Decimal)

    @property
    def full_name(self):
        return ", ".join([self.last_name.upper() or "", self.first_name or ""]).strip()

    @property
    def function_text(self):
        return Functions.get_value(self.function) if self.function else ''


@attr.s(frozen=True, slots=True)
class TutorClassRepartitionDTO(DTO):
    attribution_uuid = attr.ib(type=str)
    last_name = attr.ib(type=str)
    first_name = attr.ib(type=str)
    function = attr.ib(type=str)
    distributed_volume_to_class = attr.ib(type=Decimal)
    personal_id_number = attr.ib(type=str)
    complete_class_code = attr.ib(type=str)  # Code complet (UE + lettre classe)
    annee = attr.ib(type=int)

    @property
    def full_name(self):
        return ", ".join([self.last_name.upper() or "", self.first_name or ""]).strip()

    @property
    def function_text(self):
        return Functions.get_value(self.function) if self.function else ''
