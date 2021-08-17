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
import datetime
from typing import List, Optional

from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from ddd.logic.shared_kernel.academic_year.repository.i_academic_year import IAcademicYearRepository
from osis_common.ddd.interface import ApplicationService
from program_management.ddd.domain.academic_year import AcademicYear


class AcademicYearInMemoryRepository(IAcademicYearRepository):
    academic_years = []

    # TODO remove this and change classmethod to instance method save/search/...
    def __init__(self, academic_years: List[AcademicYear] = None):
        AcademicYearInMemoryRepository.academic_years = academic_years or []

    @classmethod
    def search(cls, entity_ids: Optional[List[AcademicYearIdentity]] = None, **kwargs) -> List[AcademicYear]:
        results = cls.academic_years
        return list(results)

    @classmethod
    def get(cls, entity_id: AcademicYearIdentity) -> AcademicYear:
        return next(academic_year for academic_year in cls.academic_years if academic_year.entity_id == entity_id)

    @classmethod
    def delete(cls, entity_id: 'AcademicYearIdentity', **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def save(cls, entity: 'AcademicYear') -> None:
        pass

    @classmethod
    def get_current(cls) -> 'AcademicYear':
        return next(
            academic_year for academic_year in cls.academic_years if academic_year.year == datetime.datetime.now().year
        )
