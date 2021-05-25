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
import uuid
from django.test import TestCase

from ddd.logic.application.commands import SearchApplicationByApplicantCommand
from ddd.logic.application.domain.model.applicant import ApplicantIdentity
from ddd.logic.application.domain.model.application import Application, ApplicationIdentity
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from infrastructure.application.repository.application_in_memory import ApplicationInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestSearchApplicationByApplicantService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.applicant_id = ApplicantIdentity(global_id='123456789')
        cls.application = Application(
            entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
            applicant_id=cls.applicant_id,
            vacant_course_id=VacantCourseIdentity(code='LAGRO1200', academic_year=AcademicYearIdentity(year=2018)),
            lecturing_volume=Decimal(5),
            practical_volume=Decimal(15),
            remark='',
            course_summary=''
        )
        cls.application_2 = Application(
            entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
            applicant_id=ApplicantIdentity(global_id='9846567895'),
            vacant_course_id=VacantCourseIdentity(code='LDROI1200', academic_year=AcademicYearIdentity(year=2018)),
            lecturing_volume=Decimal(25),
            practical_volume=Decimal(50),
            remark='',
            course_summary=''
        )
        cls.application_3 = Application(
            entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
            applicant_id=cls.applicant_id,
            vacant_course_id=VacantCourseIdentity(code='LDROI1500', academic_year=AcademicYearIdentity(year=2018)),
            lecturing_volume=Decimal(0),
            practical_volume=Decimal(5),
            remark='',
            course_summary=''
        )

        cls.application_repository = ApplicationInMemoryRepository([
            cls.application, cls.application_2, cls.application_3
        ])

    def setUp(self) -> None:
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            ApplicationRepository=lambda: self.application_repository,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_assert_search_return_result_filtered_by_applicant(self):
        cmd = SearchApplicationByApplicantCommand(global_id=self.applicant_id.global_id)

        results = self.message_bus.invoke(cmd)
        self.assertListEqual(
            results,
            [self.application, self.application_3]
        )
