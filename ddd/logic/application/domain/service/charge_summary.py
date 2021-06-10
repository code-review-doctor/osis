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

from ddd.logic.application.domain.model.applicant import Applicant
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity
from ddd.logic.application.domain.service.i_learning_unit_service import ILearningUnitService
from ddd.logic.application.dtos import ChargeSummaryDTO
from ddd.logic.application.repository.i_vacant_course_repository import IVacantCourseRepository
from osis_common.ddd import interface


class ChargeSummary(interface.DomainService):
    """
        This service aggregate multiple source in order to build the charge summary of the applicant
    """

    @classmethod
    def get(
            cls,
            application_calendar: ApplicationCalendar,
            applicant: Applicant,
            vacant_course_repository: IVacantCourseRepository,
            learning_unit_service: ILearningUnitService,
    ) -> List[ChargeSummaryDTO]:
        current_attribution = [
            attribution for attribution in applicant.attributions
            if attribution.course_id.academic_year == application_calendar.authorized_target_year
        ]

        vacant_courses_ids = [
            VacantCourseIdentity(
                code=attribution.course_id.code,
                academic_year=attribution.course_id.academic_year
            )
            for attribution in current_attribution
        ]
        vacant_courses = vacant_course_repository.search(vacant_courses_ids)

        learning_unit_ids = [attribution.course_id for attribution in applicant.attributions]
        learning_unit_volumes = learning_unit_service.search_learning_unit_volumes_dto(learning_unit_ids)

        results = []
        for attribution in current_attribution:
            vacant_course = next((vc for vc in vacant_courses if vc.code == attribution.course_id.code), None)
            learning_unit_volume = next(
                (luv for luv in learning_unit_volumes if luv.code == attribution.course_id.code),
                None
            )

            results.append(
                ChargeSummaryDTO(
                    code=attribution.course_id.code,
                    year=attribution.course_id.year,
                    title=attribution.course_title,
                    start_year=attribution.start_year.year,
                    end_year=attribution.end_year.year,
                    function=attribution.function,
                    lecturing_volume=attribution.lecturing_volume,
                    practical_volume=attribution.practical_volume,
                    lecturing_volume_available=getattr(
                        vacant_course, 'lecturing_volume_available'
                    ) if vacant_course else Decimal(0.0),
                    practical_volume_available=getattr(
                        vacant_course, 'practical_volume_available'
                    ) if vacant_course else Decimal(0.0),
                    total_lecturing_volume_course=getattr(
                        learning_unit_volume, 'lecturing_volume_total'
                    ) if learning_unit_volume else Decimal(0.0),
                    total_practical_volume_course=getattr(
                        learning_unit_volume, 'practical_volume_total'
                    ) if learning_unit_volume else Decimal(0.0),
                )
            )

        return results
