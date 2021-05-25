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

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class SearchApplicationByApplicantCommand(interface.CommandRequest):
    global_id = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class SearchVacantCoursesCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    entity_allocation_code = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class ApplyOnVacantCourseCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    global_id = attr.ib(type=str)
    lecturing_volume = attr.ib(type=Decimal)
    practical_volume = attr.ib(type=Decimal)
    course_summary = attr.ib(type=str)
    remark = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class UpdateApplicationCommand(interface.CommandRequest):
    application_id = attr.ib(type=str)
    lecturing_volume = attr.ib(type=Decimal)
    practical_volume = attr.ib(type=Decimal)
    course_summary = attr.ib(type=str)
    remark = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DeleteApplicationCommand(interface.CommandRequest):
    application_id = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class RenewMultipleAttributionsCommand(interface.CommandRequest):
    global_id = attr.ib(type=str)
    renew_codes = attr.ib(type=List[str])
