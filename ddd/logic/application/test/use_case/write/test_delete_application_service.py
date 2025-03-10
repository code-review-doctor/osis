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

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.commands import DeleteApplicationCommand
from ddd.logic.application.domain.builder.applicant_identity_builder import ApplicantIdentityBuilder
from ddd.logic.application.domain.model.applicant import Applicant
from ddd.logic.application.domain.model.application import Application, ApplicationIdentity
from ddd.logic.application.domain.model._allocation_entity import AllocationEntity
from ddd.logic.application.domain.model.vacant_course import VacantCourse, VacantCourseIdentity
from ddd.logic.application.domain.validator.exceptions import NotAuthorOfApplicationException
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from infrastructure.application.repository.applicant_in_memory import ApplicantInMemoryRepository
from infrastructure.application.repository.application_in_memory import ApplicationInMemoryRepository
from infrastructure.application.repository.vacant_course_in_memory import VacantCourseInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestDeleteApplicationService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.global_id = '123456789'
        cls.applicant = Applicant(
            entity_id=ApplicantIdentityBuilder.build_from_global_id(global_id=cls.global_id),
            first_name="Thomas",
            last_name="Durant"
        )
        cls.vacant_course = VacantCourse(
            entity_id=VacantCourseIdentity(
                code='LAGRO1500',
                academic_year=AcademicYearIdentityBuilder.build_from_year(year=2018)
            ),
            lecturing_volume_available=Decimal(10),
            practical_volume_available=Decimal(50),
            title='Introduction',
            vacant_declaration_type=VacantDeclarationType.RESEVED_FOR_INTERNS,
            is_in_team=False,
            allocation_entity=AllocationEntity(code='AGRO')
        )
        cls.applicant_repository = ApplicantInMemoryRepository([cls.applicant])
        cls.vacant_course_repository = VacantCourseInMemoryRepository([cls.vacant_course])

    def setUp(self) -> None:
        self.application = Application(
            entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
            applicant_id=self.applicant.entity_id,
            vacant_course_id=self.vacant_course.entity_id,
            lecturing_volume=Decimal(5),
            practical_volume=Decimal(15),
            remark='',
            course_summary=''
        )
        self.application_repository = ApplicationInMemoryRepository([self.application])

        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            ApplicationRepository=lambda: self.application_repository,
            ApplicantRepository=lambda: self.applicant_repository,
            VacantCourseRepository=lambda: self.vacant_course_repository
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_assert_delete_on_repository(self):
        cmd = DeleteApplicationCommand(
            application_uuid=self.application.entity_id.uuid,
            global_id=self.global_id
        )

        self.assertEqual(len(self.application_repository.applications), 1)

        self.message_bus.invoke(cmd)
        self.assertEqual(len(self.application_repository.applications), 0)

    def test_case_update_with_a_different_global_id_assert_raise_exception(self):
        cmd = DeleteApplicationCommand(
            application_uuid=self.application.entity_id.uuid,
            global_id='265656556'
        )

        with self.assertRaises(MultipleBusinessExceptions) as cm:
            self.message_bus.invoke(cmd)

        exceptions_raised = cm.exception.exceptions
        self.assertTrue(
            any([
                exception for exception in exceptions_raised
                if isinstance(exception, NotAuthorOfApplicationException)
            ])
        )
