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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime

from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYear
from ddd.logic.shared_kernel.academic_year.repository.i_academic_year import IAcademicYearRepository
from osis_common.ddd import interface


class GetCurrentAcademicYear(interface.DomainService):
    @classmethod
    def get_starting_academic_year(cls, day: datetime.date, repo: 'IAcademicYearRepository') -> 'AcademicYear':
        all_academic_years = repo.search()
        sorted_by_start_date = sorted(
            all_academic_years,
            key=lambda academic_year: academic_year.start_date,
            reverse=True
        )
        return next(
            academic_year
            for academic_year in sorted_by_start_date
            if academic_year.start_date <= day <= academic_year.end_date
        )
