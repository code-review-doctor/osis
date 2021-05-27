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
from attribution.models.enums.function import Functions
from ddd.logic.application.domain.model.attribution import Attribution
from ddd.logic.application.dtos import AttributionFromRepositoryDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from osis_common.ddd.interface import RootEntityBuilder


class AttributionBuilder(RootEntityBuilder):
    @classmethod
    def build_from_repository_dto(
            cls,
            dto: AttributionFromRepositoryDTO,
    ) -> Attribution:
        return Attribution(
            course_id=LearningUnitIdentity(
                code=dto.course_id_code,
                academic_year=AcademicYearIdentityBuilder.build_from_year(year=dto.course_id_year)
            ),
            end_year=AcademicYearIdentityBuilder.build_from_year(year=dto.end_year),
            start_year=AcademicYearIdentityBuilder.build_from_year(year=dto.start_year),
            function=Functions[dto.function] if dto.function else None,
            lecturing_volume=dto.lecturing_volume,
            practical_volume=dto.practical_volume
        )
