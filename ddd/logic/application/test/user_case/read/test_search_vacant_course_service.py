# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from decimal import Decimal

import mock
from django.test import TestCase

from base.models.enums import vacant_declaration_type
from ddd.logic.application.commands import SearchVacantCoursesCommand
from ddd.logic.application.domain.model.entity_allocation import EntityAllocation
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity, VacantCourse
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from infrastructure.application.repository.vacant_course_in_memory import VacantCourseInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestSearchVacantCourseService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vacant_course_ldroi1200 = VacantCourse(
            entity_id=VacantCourseIdentity(code='LDROI1200', academic_year=AcademicYearIdentity(year=2018)),
            lecturing_volume_available=Decimal(10),
            practical_volume_available=Decimal(50),
            title='Introduction au droit',
            vacant_declaration_type=vacant_declaration_type.RESEVED_FOR_INTERNS,
            is_in_team=False,
            entity_allocation=EntityAllocation(code='DRT')
        )
        cls.vacant_course_lagro1510 = VacantCourse(
            entity_id=VacantCourseIdentity(code='LAGRO1510', academic_year=AcademicYearIdentity(year=2018)),
            lecturing_volume_available=Decimal(50),
            practical_volume_available=Decimal(25),
            title='Introduction en agro',
            vacant_declaration_type=vacant_declaration_type.RESEVED_FOR_INTERNS,
            is_in_team=False,
            entity_allocation=EntityAllocation(code='AGRO')
        )
        cls.vacant_course_repository = VacantCourseInMemoryRepository([
            cls.vacant_course_ldroi1200, cls.vacant_course_lagro1510
        ])

    def setUp(self) -> None:
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            VacantCourseRepository=lambda: self.vacant_course_repository,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_assert_search_return_result_filtered_by_code(self):
        cmd = SearchVacantCoursesCommand(code="LDR", entity_allocation_code=None)

        results = self.message_bus.invoke(cmd)
        self.assertListEqual(results, [self.vacant_course_ldroi1200])

    def test_assert_search_return_result_filtered_by_entity_allocation(self):
        cmd = SearchVacantCoursesCommand(code=None, entity_allocation_code="AGRO")

        results = self.message_bus.invoke(cmd)
        self.assertListEqual(results, [self.vacant_course_lagro1510])
