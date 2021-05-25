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

from base.models.enums import vacant_declaration_type
from ddd.logic.application.commands import GetAttributionsAboutToExpireCommand
from ddd.logic.application.domain.model.applicant import Applicant, ApplicantIdentity
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar, ApplicationCalendarIdentity
from ddd.logic.application.domain.model.entity_allocation import EntityAllocation
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity, VacantCourse
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from infrastructure.application.repository.applicant_in_memory import ApplicantInMemoryRepository
from infrastructure.application.repository.application_calendar_in_memory import ApplicationCalendarInMemoryRepository
from infrastructure.application.repository.application_in_memory import ApplicationInMemoryRepository
from infrastructure.application.repository.vacant_course_in_memory import VacantCourseInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestGetAttributionsAboutToExpireService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.global_id = '123456789'
        cls.applicant = Applicant(
            entity_id=ApplicantIdentity(global_id=cls.global_id),
            first_name="Thomas",
            last_name="Durant",
            attributions=[]
        )
        today = datetime.date.today()
        cls.application_calendar = ApplicationCalendar(
            entity_id=ApplicationCalendarIdentity(uuid=uuid.uuid4()),
            authorized_target_year=AcademicYearIdentity(year=2018),
            start_date=today - datetime.timedelta(days=5),
            end_date=today + datetime.timedelta(days=10),
        )

        cls.vacant_course_ldroi1200 = VacantCourse(
            entity_id=VacantCourseIdentity(code='LDROI1200', academic_year=AcademicYearIdentity(year=2018)),
            lecturing_volume_available=Decimal(10),
            lecturing_volume_total=Decimal(30),
            practical_volume_available=Decimal(50),
            practical_volume_total=Decimal(50),
            title='Introduction au droit',
            vacant_declaration_type=vacant_declaration_type.RESEVED_FOR_INTERNS,
            is_in_team=False,
            entity_allocation=EntityAllocation(code='DRT')
        )
        cls.vacant_course_lagro1510 = VacantCourse(
            entity_id=VacantCourseIdentity(code='LAGRO1510', academic_year=AcademicYearIdentity(year=2018)),
            lecturing_volume_available=Decimal(50),
            lecturing_volume_total=Decimal(50),
            practical_volume_available=Decimal(25),
            practical_volume_total=Decimal(25),
            title='Introduction en agro',
            vacant_declaration_type=vacant_declaration_type.RESEVED_FOR_INTERNS,
            is_in_team=False,
            entity_allocation=EntityAllocation(code='AGRO')
        )

    def setUp(self) -> None:
        self.applicant_repository = ApplicantInMemoryRepository([self.applicant])
        self.application_calendar_repository = ApplicationCalendarInMemoryRepository([self.application_calendar])
        self.vacant_course_repository = VacantCourseInMemoryRepository([
            self.vacant_course_ldroi1200, self.vacant_course_lagro1510
        ])
        self.application_repository = ApplicationInMemoryRepository([])

        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            ApplicationRepository=lambda: self.application_repository,
            ApplicantRepository=lambda: self.applicant_repository,
            VacantCourseRepository=lambda: self.vacant_course_repository,
            ApplicationCalendarRepository=lambda: self.application_calendar_repository
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_case_attributions_about_to_expire_is_empty(self):
        self.applicant.attributions = []

        cmd = GetAttributionsAboutToExpireCommand(global_id=self.global_id)
        results = self.message_bus.invoke(cmd)

        self.assertListEqual(results, [])
