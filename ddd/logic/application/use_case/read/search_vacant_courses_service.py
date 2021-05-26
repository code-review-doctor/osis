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

from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.commands import SearchVacantCoursesCommand
from ddd.logic.application.domain.model.entity_allocation import EntityAllocation
from ddd.logic.application.domain.model.vacant_course import VacantCourse
from ddd.logic.application.repository.i_application_calendar_repository import IApplicationCalendarRepository
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository


def search_vacant_courses(
        cmd: SearchVacantCoursesCommand,
        application_calendar_repository: IApplicationCalendarRepository,
        vacant_course_repository: IVacantCourseRepository
) -> List[VacantCourse]:
    # Given
    application_calendar = application_calendar_repository.get_current_application_calendar()
    entity_allocation = EntityAllocation(code=cmd.entity_allocation_code) if cmd.entity_allocation_code else None
    vacant_declaration_types = [
        VacantDeclarationType[vacant_declaration_str] for vacant_declaration_str in cmd.vacant_declaration_types
    ] if cmd.vacant_declaration_types else None

    return vacant_course_repository.search(
        code=cmd.code,
        academic_year_id=application_calendar.authorized_target_year,
        entity_allocation=entity_allocation,
        vacant_declaration_types=vacant_declaration_types
    )
