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
from typing import List

import attr

from ddd.logic.learning_unit.dtos import EffectiveClassFromRepositoryDTO
from osis_common.ddd.interface import DTO


@attr.s(frozen=True, slots=True)
class AcademicYearDataDTO(DTO):
    year = attr.ib(type=str)
    start_date = attr.ib(type=datetime.date)
    end_date = attr.ib(type=datetime.date)


@attr.s(frozen=True, slots=True)
class LearningUnitAttributionFromRepositoryDTO(DTO):
    function = attr.ib(type=str)
    attribution_uuid = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)
    effective_classes = attr.ib(type=List[EffectiveClassFromRepositoryDTO])
    attribution_volume = attr.ib(type=float)


@attr.s(frozen=True, slots=True)
class TutorSearchDTO(DTO):
    last_name = attr.ib(type=str)
    first_name = attr.ib(type=str)
    personal_id_number = attr.ib(type=str)
    attributions = attr.ib(type=List[LearningUnitAttributionFromRepositoryDTO])


@attr.s(frozen=True, slots=True)
class DistributedEffectiveClassesDTO(DTO):
    class_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class TutorAttributionToLearningUnitDTO(DTO):
    last_name = attr.ib(type=str)
    first_name = attr.ib(type=str)
    personal_id_number = attr.ib(type=str)
    function = attr.ib(type=str)
    attributed_volume_to_learning_unit = attr.ib(type=float)
