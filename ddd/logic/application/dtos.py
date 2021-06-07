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
from typing import List

import attr

from osis_common.ddd.interface import DTO


@attr.s(frozen=True, slots=True)
class AttributionFromRepositoryDTO(DTO):
    course_id_code = attr.ib(type=str)
    course_id_year = attr.ib(type=int)
    course_title = attr.ib(type=int)
    applicant_id_global_id = attr.ib(type=str)
    function = attr.ib(type=str)
    end_year = attr.ib(type=int)
    start_year = attr.ib(type=int)
    lecturing_volume = attr.ib(type=Decimal)
    practical_volume = attr.ib(type=Decimal)


@attr.s(frozen=True, slots=True)
class ApplicantFromRepositoryDTO(DTO):
    first_name = attr.ib(type=str)
    last_name = attr.ib(type=str)
    global_id = attr.ib(type=str)
    attributions = attr.ib(type=List[AttributionFromRepositoryDTO], default=[])


@attr.s(frozen=True, slots=True)
class VacantCourseFromRepositoryDTO(DTO):
    code = attr.ib(type=str)
    year = attr.ib(type=int)
    title = attr.ib(type=str)
    is_in_team = attr.ib(type=bool)
    allocation_entity = attr.ib(type=str)
    vacant_declaration_type = attr.ib(type=str)
    lecturing_volume_total = attr.ib(type=Decimal)
    lecturing_volume_available = attr.ib(type=Decimal)
    practical_volume_total = attr.ib(type=Decimal)
    practical_volume_available = attr.ib(type=Decimal)


@attr.s(frozen=True, slots=True)
class ApplicationFromRepositoryDTO(DTO):
    uuid = attr.ib(type=str)
    applicant_global_id = attr.ib(type=str)
    vacant_course_code = attr.ib(type=str)
    vacant_course_year = attr.ib(type=int)
    lecturing_volume = attr.ib(type=Decimal)
    practical_volume = attr.ib(type=Decimal)
    remark = attr.ib(type=str)
    course_summary = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class AttributionAboutToExpireDTO(DTO):
    code = attr.ib(type=str)
    year = attr.ib(type=int)
    title = attr.ib(type=str)
    lecturing_volume = attr.ib(type=Decimal)
    practical_volume = attr.ib(type=Decimal)
    function = attr.ib(type=str)
    end_year = attr.ib(type=int)
    start_year = attr.ib(type=int)
    total_lecturing_volume_course = attr.ib(type=Decimal)
    total_practical_volume_course = attr.ib(type=Decimal)
    lecturing_volume_available = attr.ib(type=Decimal)
    practical_volume_available = attr.ib(type=Decimal)
    unavailable_renewal_reason = attr.ib(type=str)
    is_renewable = attr.ib(type=bool)


@attr.s(frozen=True, slots=True)
class ApplicationByApplicantDTO(DTO):
    uuid = attr.ib(type=str)
    code = attr.ib(type=str)
    year = attr.ib(type=int)
    lecturing_volume = attr.ib(type=Decimal)
    practical_volume = attr.ib(type=Decimal)
    remark = attr.ib(type=str)
    course_summary = attr.ib(type=str)
