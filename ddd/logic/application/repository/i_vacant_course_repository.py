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
import abc
from typing import List, Optional

from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity, VacantCourse
from ddd.logic.application.dtos import VacantCourseSearchDTO
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from osis_common.ddd import interface
from osis_common.ddd.interface import ApplicationService


class IVacantCourseRepository(interface.AbstractRepository):
    @classmethod
    @abc.abstractmethod
    def get(cls, entity_id: VacantCourseIdentity) -> VacantCourse:
        pass

    @classmethod
    @abc.abstractmethod
    def search(cls, entity_ids: Optional[List[VacantCourseIdentity]] = None, **kwargs) -> List[VacantCourse]:
        pass

    @classmethod
    @abc.abstractmethod
    def search_vacant_course_dto(
            cls,
            code: str = None,
            academic_year_id: AcademicYearIdentity = None,
            allocation_entity_code: str = None,
            with_allocation_entity_children: bool = False,
            vacant_declaration_types: List[VacantDeclarationType] = None,
            **kwargs
    ) -> List[VacantCourseSearchDTO]:
        pass

    @classmethod
    def delete(cls, entity_id: VacantCourseIdentity, **kwargs: ApplicationService) -> None:
        raise NotImplementedError

    @classmethod
    def save(cls, entity: VacantCourse) -> None:
        raise NotImplementedError
