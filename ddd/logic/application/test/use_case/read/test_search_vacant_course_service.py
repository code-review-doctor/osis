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
import datetime
from decimal import Decimal

import mock
import uuid
from django.test import TestCase

from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.commands import SearchVacantCoursesCommand
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar, ApplicationCalendarIdentity
from ddd.logic.application.domain.model.allocation_entity import AllocationEntity
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity, VacantCourse
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from infrastructure.application.repository.application_calendar_in_memory import ApplicationCalendarInMemoryRepository
from infrastructure.application.repository.vacant_course_in_memory import VacantCourseInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestSearchVacantCourseService(TestCase):
    @classmethod
    def setUpTestData(cls):
        today = datetime.date.today()
        cls.application_calendar = ApplicationCalendar(
            entity_id=ApplicationCalendarIdentity(uuid=uuid.uuid4()),
            authorized_target_year=AcademicYearIdentityBuilder.build_from_year(year=2018),
            start_date=today - datetime.timedelta(days=5),
            end_date=today + datetime.timedelta(days=10),
        )

        cls.vacant_course_ldroi1200 = VacantCourse(
            entity_id=VacantCourseIdentity(
                code='LDROI1200',
                academic_year=cls.application_calendar.authorized_target_year
            ),
            lecturing_volume_available=Decimal(10),
            lecturing_volume_total=Decimal(30),
            practical_volume_available=Decimal(50),
            practical_volume_total=Decimal(50),
            title='Introduction au droit',
            vacant_declaration_type=VacantDeclarationType.RESEVED_FOR_INTERNS,
            is_in_team=False,
            allocation_entity=AllocationEntity(code='DRT')
        )
        cls.vacant_course_lagro1510 = VacantCourse(
            entity_id=VacantCourseIdentity(
                code='LAGRO1510',
                academic_year=cls.application_calendar.authorized_target_year
            ),
            lecturing_volume_available=Decimal(50),
            lecturing_volume_total=Decimal(50),
            practical_volume_available=Decimal(25),
            practical_volume_total=Decimal(25),
            title='Introduction en agro',
            vacant_declaration_type=VacantDeclarationType.OPEN_FOR_EXTERNS,
            is_in_team=False,
            allocation_entity=AllocationEntity(code='AGRO')
        )

        cls.application_calendar_repository = ApplicationCalendarInMemoryRepository([cls.application_calendar])
        cls.vacant_course_repository = VacantCourseInMemoryRepository([
            cls.vacant_course_ldroi1200, cls.vacant_course_lagro1510
        ])

    def setUp(self) -> None:
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            VacantCourseRepository=lambda: self.vacant_course_repository,
            ApplicationCalendarRepository=lambda: self.application_calendar_repository
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_assert_search_return_result_filtered_by_code(self):
        cmd = SearchVacantCoursesCommand(code="LDR", allocation_entity_code=None, vacant_declaration_types=None)

        results = self.message_bus.invoke(cmd)
        self.assertListEqual(results, [self.vacant_course_ldroi1200])

    def test_assert_search_return_result_filtered_by_allocation_entity(self):
        cmd = SearchVacantCoursesCommand(code=None, allocation_entity_code="AGRO", vacant_declaration_types=None)

        results = self.message_bus.invoke(cmd)
        self.assertListEqual(results, [self.vacant_course_lagro1510])

    def test_assert_search_return_result_filtered_by_vacant_declaration_types(self):
        cmd = SearchVacantCoursesCommand(
            code=None,
            allocation_entity_code=None,
            vacant_declaration_types=[VacantDeclarationType.OPEN_FOR_EXTERNS.name]
        )

        results = self.message_bus.invoke(cmd)
        self.assertListEqual(results, [self.vacant_course_lagro1510])
