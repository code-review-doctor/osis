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

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.commands import ApplyOnVacantCourseCommand
from ddd.logic.application.domain.builder.applicant_identity_builder import ApplicantIdentityBuilder
from ddd.logic.application.domain.model.applicant import Applicant
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar, ApplicationCalendarIdentity
from ddd.logic.application.domain.model.allocation_entity import AllocationEntity
from ddd.logic.application.domain.model.vacant_course import VacantCourse, VacantCourseIdentity
from ddd.logic.application.domain.validator.exceptions import LecturingAndPracticalChargeNotFilledException, \
    ApplicationAlreadyExistsException, VolumesAskedShouldBeLowerOrEqualToVolumeAvailable
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from infrastructure.application.repository.applicant_in_memory import ApplicantInMemoryRepository
from infrastructure.application.repository.application_calendar_in_memory import ApplicationCalendarInMemoryRepository
from infrastructure.application.repository.application_in_memory import ApplicationInMemoryRepository
from infrastructure.application.repository.vacant_course_in_memory import VacantCourseInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestApplyOnVacantCourseService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.applicant = Applicant(
            entity_id=ApplicantIdentityBuilder.build_from_global_id(global_id='123456789'),
            first_name="Thomas",
            last_name="Durant"
        )
        today = datetime.date.today()
        cls.application_calendar = ApplicationCalendar(
            entity_id=ApplicationCalendarIdentity(uuid=uuid.uuid4()),
            authorized_target_year=AcademicYearIdentityBuilder.build_from_year(year=2018),
            start_date=today - datetime.timedelta(days=5),
            end_date=today + datetime.timedelta(days=10),
        )
        cls.vacant_course = VacantCourse(
            entity_id=VacantCourseIdentity(
                code='LDROI1200',
                academic_year=AcademicYearIdentityBuilder.build_from_year(year=2018)
            ),
            lecturing_volume_available=Decimal(10),
            practical_volume_available=Decimal(50),
            title='Introduction au droit',
            vacant_declaration_type=VacantDeclarationType.RESEVED_FOR_INTERNS,
            is_in_team=False,
            allocation_entity=AllocationEntity(code='DRT')
        )

        cls.applicant_repository = ApplicantInMemoryRepository([cls.applicant])
        cls.application_calendar_repository = ApplicationCalendarInMemoryRepository([cls.application_calendar])
        cls.vacant_course_repository = VacantCourseInMemoryRepository([cls.vacant_course])
        cls.application_repository = ApplicationInMemoryRepository([])

    def setUp(self) -> None:
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

    def test_case_both_volume_not_provided_in_command_assert_not_filled_exception_raised(self):
        cmd = ApplyOnVacantCourseCommand(
            code='LDROI1200',
            global_id='123456789',
            lecturing_volume=None,
            practical_volume=None,
            course_summary='Résumé du cours',
            remark='Remarque personelle',
        )

        with self.assertRaises(MultipleBusinessExceptions) as cm:
            self.message_bus.invoke(cmd)

        exceptions_raised = cm.exception.exceptions
        self.assertTrue(
            any([
                exception for exception in exceptions_raised
                if isinstance(exception, LecturingAndPracticalChargeNotFilledException)
            ])
        )

    def test_case_both_volume_set_to_zero_in_command_assert_not_filled_exception_raised(self):
        cmd = ApplyOnVacantCourseCommand(
            code='LDROI1200',
            global_id='123456789',
            lecturing_volume=Decimal(0),
            practical_volume=Decimal(0),
            course_summary='Résumé du cours',
            remark='Remarque personelle',
        )
        with self.assertRaises(MultipleBusinessExceptions) as cm:
            self.message_bus.invoke(cmd)

        exceptions_raised = cm.exception.exceptions
        self.assertTrue(
            any([
                exception for exception in exceptions_raised
                if isinstance(exception, LecturingAndPracticalChargeNotFilledException)
            ])
        )

    def test_case_apply_on_vacant_course_which_have_been_already_applied_assert_raise_exception(self):
        cmd = ApplyOnVacantCourseCommand(
            code='LDROI1200',
            global_id='123456789',
            lecturing_volume=Decimal(10),
            practical_volume=Decimal(0),
            course_summary='Résumé du cours',
            remark='Remarque personelle',
        )

        self.message_bus.invoke(cmd)
        self.assertEqual(len(self.application_repository.applications), 1)

        with self.assertRaises(MultipleBusinessExceptions) as cm:
            self.message_bus.invoke(cmd)
        exceptions_raised = cm.exception.exceptions
        self.assertTrue(
            any([
                exception for exception in exceptions_raised
                if isinstance(exception, ApplicationAlreadyExistsException)
            ])
        )

    def test_case_apply_on_vacant_course_with_practical_volume_greater_than_available_assert_raise_exception(self):
        cmd = ApplyOnVacantCourseCommand(
            code='LDROI1200',
            global_id='123456789',
            lecturing_volume=Decimal(10),
            practical_volume=Decimal(60),   # Available 50
            course_summary='Résumé du cours',
            remark='Remarque personelle',
        )

        with self.assertRaises(MultipleBusinessExceptions) as cm:
            self.message_bus.invoke(cmd)
        exceptions_raised = cm.exception.exceptions
        self.assertTrue(
            any([
                exception for exception in exceptions_raised
                if isinstance(exception, VolumesAskedShouldBeLowerOrEqualToVolumeAvailable)
            ])
        )

    def test_case_apply_on_vacant_course_with_lecturing_volume_greater_than_available_assert_raise_exception(self):
        cmd = ApplyOnVacantCourseCommand(
            code='LDROI1200',
            global_id='123456789',
            lecturing_volume=Decimal(25),   # Available 10
            practical_volume=Decimal(0),
            course_summary='Résumé du cours',
            remark='Remarque personelle',
        )

        with self.assertRaises(MultipleBusinessExceptions) as cm:
            self.message_bus.invoke(cmd)
        exceptions_raised = cm.exception.exceptions
        self.assertTrue(
            any([
                exception for exception in exceptions_raised
                if isinstance(exception, VolumesAskedShouldBeLowerOrEqualToVolumeAvailable)
            ])
        )
