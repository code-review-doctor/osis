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
from typing import List, Optional

from attribution.models.enums.function import Functions
from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar
from ddd.logic.application.domain.service.i_learning_unit_service import ILearningUnitService
from ddd.logic.application.dtos import VacantCourseSearchDTO, TutorAttributionDTO
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from osis_common.ddd import interface


class VacantCourseSearcher(interface.DomainService):
    @classmethod
    def search(
            cls,
            code: Optional[str],
            application_calendar: ApplicationCalendar,
            allocation_entity_code: Optional[str],
            vacant_declaration_types: List[VacantDeclarationType],
            vacant_course_repository: IVacantCourseRepository,
            learning_unit_service: ILearningUnitService
    ) -> List[VacantCourseSearchDTO]:
        vacant_courses_dto = vacant_course_repository.search_vacant_course_dto(
            code=code,
            academic_year_id=application_calendar.authorized_target_year,
            allocation_entity_code=allocation_entity_code,
            vacant_declaration_types=vacant_declaration_types
        )
        if not vacant_courses_dto:
            return []

        learning_unit_entity_ids = [
            LearningUnitIdentity(
                academic_year=AcademicYearIdentityBuilder.build_from_year(vc.year),
                code=vc.code
            ) for vc in vacant_courses_dto
        ]
        learning_units_volumes = learning_unit_service.search_learning_unit_volumes_dto(learning_unit_entity_ids)
        learning_units_tutors = learning_unit_service.search_tutor_attribution_dto(learning_unit_entity_ids)

        results = []
        for vacant_course_dto in vacant_courses_dto:
            learning_unit_volume = next(
                (luv for luv in learning_units_volumes if luv.code == vacant_course_dto.code),
                None
            )
            tutors_filtered = [
                TutorAttributionDTO(
                    first_name=t_dto.first_name,
                    last_name=t_dto.last_name,
                    function=Functions[t_dto.function] if t_dto.function else None,
                    lecturing_volume=t_dto.lecturing_volume,
                    practical_volume=t_dto.practical_volume,
                ) for t_dto in learning_units_tutors if t_dto.code == vacant_course_dto.code
            ]

            results.append(
                VacantCourseSearchDTO(
                    code=vacant_course_dto.code,
                    year=vacant_course_dto.year,
                    title=vacant_course_dto.title,
                    is_in_team=vacant_course_dto.is_in_team,
                    allocation_entity_code=vacant_course_dto.allocation_entity_code,
                    vacant_declaration_type=vacant_course_dto.vacant_declaration_type,
                    lecturing_volume_total=getattr(
                        learning_unit_volume, 'lecturing_volume_total'
                    ) if learning_unit_volume else Decimal(0.0),
                    lecturing_volume_available=vacant_course_dto.lecturing_volume_available,
                    practical_volume_total=getattr(
                        learning_unit_volume, 'practical_volume_total'
                    ) if learning_unit_volume else Decimal(0.0),
                    practical_volume_available=vacant_course_dto.practical_volume_available,
                    tutors=tutors_filtered,
                )
            )
        return results
