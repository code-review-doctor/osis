#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.test import SimpleTestCase

from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYear, AcademicYearIdentity
from infrastructure.shared_kernel.academic_year.repository.in_memory.academic_year import AcademicYearInMemoryRepository


class TestAcademicYearInMemoryRepository(SimpleTestCase):
    def setUp(self):
        self.academic_year_repository = AcademicYearInMemoryRepository()

        for annee in range(2016, 2021):
            self.academic_year_repository.save(AcademicYear(
                entity_id=AcademicYearIdentity(year=annee),
                start_date=datetime.date(annee, 9, 15),
                end_date=datetime.date(annee+1, 9, 30),
            ))

    def test_search_should_return_specific_academic_years_if_specified_year(self):
        years = self.academic_year_repository.search(year=2018)

        self.assertEqual(len(years), 3)

        for index, annee in enumerate(range(2018, 2021)):
            self.assertEqual(years[index].year, annee)

    def test_search_should_return_all_academic_years_if_not_specified_year(self):
        years = self.academic_year_repository.search()

        self.assertEqual(len(years), 5)

        for index, annee in enumerate(range(2016, 2021)):
            self.assertEqual(years[index].year, annee)
