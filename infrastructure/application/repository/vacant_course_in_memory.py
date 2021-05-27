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

from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.domain.model.allocation_entity import AllocationEntity
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity, VacantCourse
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity


class VacantCourseInMemoryRepository(IVacantCourseRepository):
    vacant_courses = []

    # TODO remove this and change classmethod to instance method save/search/...
    def __init__(self, vacant_courses: List[VacantCourse] = None):
        VacantCourseInMemoryRepository.vacant_courses = vacant_courses or []

    @classmethod
    def search(
            cls,
            entity_ids: Optional[List[VacantCourseIdentity]] = None,
            code: str = None,
            academic_year_id: AcademicYearIdentity = None,
            allocation_entity: AllocationEntity = None,
            with_allocation_entity_children: bool = False,
            vacant_declaration_types: List[VacantDeclarationType] = None,
            **kwargs
    ) -> List[VacantCourse]:
        results = cls.vacant_courses
        if entity_ids:
            results = filter(lambda vacant_course: vacant_course.entity_id in entity_ids, results)
        if code is not None:
            results = filter(lambda vacant_course: code in vacant_course.code, results)
        if academic_year_id is not None:
            results = filter(lambda vacant_course: academic_year_id.year == vacant_course.year, results)
        if allocation_entity is not None:
            results = filter(lambda vacant_course: vacant_course.allocation_entity == allocation_entity, results)
        if vacant_declaration_types is not None:
            results = filter(
                lambda vacant_course: vacant_course.vacant_declaration_type in vacant_declaration_types, results
            )
        return list(results)

    @classmethod
    def get(cls, entity_id: VacantCourseIdentity) -> VacantCourse:
        return next(vacant_course for vacant_course in cls.vacant_courses if vacant_course.entity_id == entity_id)
