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

from ddd.logic.application.commands import SearchApplicationByApplicantCommand
from ddd.logic.application.domain.builder.applicant_identity_builder import ApplicantIdentityBuilder
from ddd.logic.application.domain.model.application import Application, ApplicationIdentity
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar, ApplicationCalendarIdentity
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity
from ddd.logic.application.dtos import ApplicationByApplicantDTO
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from infrastructure.application.repository.application_calendar_in_memory import ApplicationCalendarInMemoryRepository
from infrastructure.application.repository.application_in_memory import ApplicationInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestSearchApplicationByApplicantService(TestCase):
    @classmethod
    def setUpTestData(cls):
        today = datetime.date.today()
        cls.application_calendar = ApplicationCalendar(
            entity_id=ApplicationCalendarIdentity(uuid=uuid.uuid4()),
            authorized_target_year=AcademicYearIdentityBuilder.build_from_year(year=2018),
            start_date=today - datetime.timedelta(days=5),
            end_date=today + datetime.timedelta(days=10),
        )

        cls.applicant_id = ApplicantIdentityBuilder.build_from_global_id(global_id='123456789')
        cls.application = Application(
            entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
            applicant_id=cls.applicant_id,
            vacant_course_id=VacantCourseIdentity(
                code='LAGRO1200',
                academic_year=cls.application_calendar.authorized_target_year
            ),
            lecturing_volume=Decimal(5),
            practical_volume=Decimal(15),
            remark='',
            course_summary=''
        )
        cls.application_2 = Application(
            entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
            applicant_id=ApplicantIdentityBuilder.build_from_global_id(global_id='9846567895'),
            vacant_course_id=VacantCourseIdentity(
                code='LDROI1200',
                academic_year=cls.application_calendar.authorized_target_year
            ),
            lecturing_volume=Decimal(25),
            practical_volume=Decimal(50),
            remark='',
            course_summary=''
        )
        cls.application_3 = Application(
            entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
            applicant_id=cls.applicant_id,
            vacant_course_id=VacantCourseIdentity(
                code='LDROI1500',
                academic_year=cls.application_calendar.authorized_target_year
            ),
            lecturing_volume=Decimal(0),
            practical_volume=Decimal(5),
            remark='',
            course_summary=''
        )

        cls.application_calendar_repository = ApplicationCalendarInMemoryRepository([cls.application_calendar])
        cls.application_repository = ApplicationInMemoryRepository([
            cls.application, cls.application_2, cls.application_3
        ])

    def setUp(self) -> None:
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            ApplicationRepository=lambda: self.application_repository,
            ApplicationCalendarRepository=lambda: self.application_calendar_repository
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_assert_search_return_result_filtered_by_applicant(self):
        cmd = SearchApplicationByApplicantCommand(global_id=self.applicant_id.global_id)

        results = self.message_bus.invoke(cmd)
        self.assertListEqual(
            results,
            [
                ApplicationByApplicantDTO(
                    uuid=self.application.entity_id.uuid,
                    code=self.application.vacant_course_id.code,
                    year=self.application.vacant_course_id.year,
                    lecturing_volume=self.application.lecturing_volume,
                    lecturing_volume_available=self.application.lecturing_volume,
                    practical_volume=self.application.practical_volume,
                    practical_volume_available=self.application.practical_volume,
                    remark=self.application.remark,
                    course_summary=self.application.course_summary,
                    course_title=""
                ),
                ApplicationByApplicantDTO(
                    uuid=self.application_3.entity_id.uuid,
                    code=self.application_3.vacant_course_id.code,
                    year=self.application_3.vacant_course_id.year,
                    lecturing_volume=self.application_3.lecturing_volume,
                    lecturing_volume_available=self.application_3.lecturing_volume,
                    practical_volume=self.application_3.practical_volume,
                    practical_volume_available=self.application_3.practical_volume,
                    remark=self.application_3.remark,
                    course_summary=self.application_3.course_summary,
                    course_title=""
                )
            ]
        )
