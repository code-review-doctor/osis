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
from ddd.logic.application.domain.service.i_learning_unit_service import ILearningUnitService
from ddd.logic.application.domain.service.vacant_course_searcher import VacantCourseSearcher
from ddd.logic.application.dtos import VacantCourseSearchDTO
from ddd.logic.application.repository.i_application_calendar_repository import IApplicationCalendarRepository
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository


def search_vacant_courses(
        cmd: SearchVacantCoursesCommand,
        application_calendar_repository: IApplicationCalendarRepository,
        vacant_course_repository: IVacantCourseRepository,
        learning_unit_service: ILearningUnitService
) -> List[VacantCourseSearchDTO]:
    # Given
    application_calendar = application_calendar_repository.get_current_application_calendar()
    vacant_declaration_types = [
        VacantDeclarationType[vacant_declaration_str] for vacant_declaration_str in cmd.vacant_declaration_types
    ] if cmd.vacant_declaration_types else None

    return VacantCourseSearcher.search(
        code=cmd.code,
        application_calendar=application_calendar,
        allocation_entity_code=cmd.allocation_entity_code,
        vacant_declaration_types=vacant_declaration_types,
        vacant_course_repository=vacant_course_repository,
        learning_unit_service=learning_unit_service
    )
