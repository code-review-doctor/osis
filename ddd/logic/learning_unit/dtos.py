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
from typing import List, Optional

import attr

from ddd.logic.learning_unit.domain.model._financial_volumes_repartition import DurationUnit
from ddd.logic.learning_unit.domain.model.responsible_entity import EntityCode
from osis_common.ddd.interface import DTO


@attr.s(frozen=True, slots=True)
class PartimFromRepositoryDTO(DTO):
    subdivision = attr.ib(type=str)
    title_fr = attr.ib(type=str)
    title_en = attr.ib(type=str)
    credits = attr.ib(type=int)
    periodicity = attr.ib(type=str)
    iso_code = attr.ib(type=str)
    remark_faculty = attr.ib(type=str)
    remark_publication_fr = attr.ib(type=str)
    remark_publication_en = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class LearningUnitFromRepositoryDTO(DTO):
    code = attr.ib(type=str)
    year = attr.ib(type=int)
    type = attr.ib(type=str)
    common_title_fr = attr.ib(type=str)
    specific_title_fr = attr.ib(type=str)
    common_title_en = attr.ib(type=str)
    specific_title_en = attr.ib(type=str)
    credits = attr.ib(type=int)
    internship_subtype = attr.ib(type=str)
    responsible_entity_code = attr.ib(type=EntityCode)
    attribution_entity_code = attr.ib(type=EntityCode)
    periodicity = attr.ib(type=str)
    iso_code = attr.ib(type=str)
    remark_faculty = attr.ib(type=str)
    remark_publication_fr = attr.ib(type=str)
    remark_publication_en = attr.ib(type=str)

    repartition_entity_2 = attr.ib(type=Optional[EntityCode])
    repartition_entity_3 = attr.ib(type=Optional[EntityCode])

    practical_volume_q1 = attr.ib(type=DurationUnit)
    practical_volume_q2 = attr.ib(type=DurationUnit)
    practical_volume_annual = attr.ib(type=DurationUnit)
    practical_planned_classes = attr.ib(type=int)
    practical_volume_repartition_responsible_entity = attr.ib(type=Optional[DurationUnit])
    practical_volume_repartition_entity_2 = attr.ib(type=Optional[DurationUnit])
    practical_volume_repartition_entity_3 = attr.ib(type=Optional[DurationUnit])

    lecturing_volume_q1 = attr.ib(type=DurationUnit)
    lecturing_volume_q2 = attr.ib(type=DurationUnit)
    lecturing_volume_annual = attr.ib(type=DurationUnit)
    lecturing_planned_classes = attr.ib(type=int)
    lecturing_volume_repartition_responsible_entity = attr.ib(type=Optional[DurationUnit])
    lecturing_volume_repartition_entity_2 = attr.ib(type=Optional[DurationUnit])
    lecturing_volume_repartition_entity_3 = attr.ib(type=Optional[DurationUnit])

    derogation_quadrimester = attr.ib(type=str)
    derogation_session = attr.ib(type=str)
    partims = attr.ib(type=List[PartimFromRepositoryDTO])
    teaching_place_uuid = attr.ib(type=str)
    professional_integration = attr.ib(type=bool)
    is_active = attr.ib(type=bool)
    learning_unit_type = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class LearningUnitSearchDTO(DTO):
    year = attr.ib(type=int)
    code = attr.ib(type=str)
    full_title = attr.ib(type=str)
    type = attr.ib(type=str)
    responsible_entity_code = attr.ib(type=str)
    responsible_entity_title = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class UclEntityDataDTO(DTO):
    code = attr.ib(type=str)
    type = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class EffectiveClassFromRepositoryDTO(DTO):
    class_code = attr.ib(type=str)
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)
    title_fr = attr.ib(type=str)
    title_en = attr.ib(type=str)
    teaching_place_uuid = attr.ib(type=str)
    derogation_quadrimester = attr.ib(type=str)
    session_derogation = attr.ib(type=str)
    volume_q1 = attr.ib(type=DurationUnit)
    volume_q2 = attr.ib(type=DurationUnit)
    class_type = attr.ib(type=str)
