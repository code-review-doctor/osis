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
import copy
from datetime import datetime
from decimal import Decimal

import mock
import uuid
from django.test import TestCase

from attribution.models.enums import function
from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums import vacant_declaration_type
from ddd.logic.application.commands import RenewMultipleAttributionsCommand
from ddd.logic.application.domain.model.applicant import Applicant, ApplicantIdentity
from ddd.logic.application.domain.model.application import Application, ApplicationIdentity
from ddd.logic.application.domain.model.attribution import Attribution
from ddd.logic.application.domain.model.entity_allocation import EntityAllocation
from ddd.logic.application.domain.model.vacant_course import VacantCourse, VacantCourseIdentity
from ddd.logic.application.domain.validator.exceptions import AttributionAboutToExpireNotFound, \
    VolumesAskedShouldBeLowerOrEqualToVolumeAvailable, ApplicationAlreadyExistsException
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from infrastructure.application.repository.applicant_in_memory import ApplicantInMemoryRepository
from infrastructure.application.repository.application_in_memory import ApplicationInMemoryRepository
from infrastructure.application.repository.vacant_course_in_memory import VacantCourseInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestRenewMultipleAttributionsService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_year = datetime.now().year  # FIXME : Use event calendar with data_year
        cls.attribution_about_to_expire = Attribution(
            course_id=LearningUnitIdentity(code='LDROI1200', academic_year=AcademicYearIdentity(year=2018)),
            function=function.HOLDER,
            end_year=AcademicYearIdentity(cls.current_year),
            lecturing_volume=Decimal(5),
            practical_volume=None,
        )

        cls.global_id = '123456789'
        cls.applicant = Applicant(
            entity_id=ApplicantIdentity(global_id=cls.global_id),
            first_name="Thomas",
            last_name="Durant",
            attributions=[cls.attribution_about_to_expire]
        )
        cls.vacant_course = VacantCourse(
            entity_id=VacantCourseIdentity(
                code='LDROI1200',
                academic_year=AcademicYearIdentity(year=cls.current_year + 1)
            ),
            lecturing_volume_available=Decimal(10),
            practical_volume_available=Decimal(50),
            title='Introduction au droit',
            vacant_declaration_type=vacant_declaration_type.RESEVED_FOR_INTERNS,
            is_in_team=False,
            entity_allocation=EntityAllocation(code='DRT')
        )

    def setUp(self) -> None:
        self.applicant_repository = ApplicantInMemoryRepository([self.applicant])
        self.vacant_course_repository = VacantCourseInMemoryRepository([self.vacant_course])
        self.application_repository = ApplicationInMemoryRepository([])

        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            ApplicationRepository=lambda: self.application_repository,
            ApplicantRepository=lambda: self.applicant_repository,
            VacantCourseRepository=lambda: self.vacant_course_repository
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_assert_renewal_is_correctly_processed(self):
        cmd = RenewMultipleAttributionsCommand(global_id=self.global_id, renew_codes=['LDROI1200'])
        self.message_bus.invoke(cmd)

        self.assertEqual(
            len(self.application_repository.search(applicant_id=self.applicant.entity_id)),
            1
        )

    def test_renewal_multiple_case_one_not_about_to_renewal_assert_applications_not_created_at_all(self):
        cmd = RenewMultipleAttributionsCommand(global_id=self.global_id, renew_codes=['LDROI1200', 'LDROI2500'])

        with self.assertRaises(MultipleBusinessExceptions) as cm:
            self.message_bus.invoke(cmd)

        exceptions_raised = cm.exception.exceptions
        self.assertTrue(
            any([
                exception for exception in exceptions_raised
                if isinstance(exception, AttributionAboutToExpireNotFound)
            ])
        )

        self.assertEqual(
            len(self.application_repository.search(applicant_id=self.applicant.entity_id)),
            0
        )

    def test_renewal_multiple_case_vacant_course_with_less_availability_than_attribution_assert_raise_exception(self):
        vacant_course_with_less_availability = copy.deepcopy(self.vacant_course)
        vacant_course_with_less_availability.practical_volume_available = Decimal(1)
        vacant_course_with_less_availability.lecturing_volume_available = Decimal(1)
        self.vacant_course_repository = VacantCourseInMemoryRepository([vacant_course_with_less_availability])

        cmd = RenewMultipleAttributionsCommand(global_id=self.global_id, renew_codes=['LDROI1200'])
        with self.assertRaises(MultipleBusinessExceptions) as cm:
            self.message_bus.invoke(cmd)

        exceptions_raised = cm.exception.exceptions
        self.assertTrue(
            any([
                exception for exception in exceptions_raised
                if isinstance(exception, VolumesAskedShouldBeLowerOrEqualToVolumeAvailable)
            ])
        )

    def test_renewal_multiple_case_already_applied_on_course_assert_raise_exception(self):
        application = Application(
            entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
            applicant_id=self.applicant.entity_id,
            vacant_course_id=self.vacant_course.entity_id,
            lecturing_volume=self.vacant_course.lecturing_volume_available,
            practical_volume=self.vacant_course.practical_volume_available,
            remark='',
            course_summary='',
        )
        self.application_repository = ApplicationInMemoryRepository([application])

        cmd = RenewMultipleAttributionsCommand(global_id=self.global_id, renew_codes=['LDROI1200'])
        with self.assertRaises(MultipleBusinessExceptions) as cm:
            self.message_bus.invoke(cmd)

        exceptions_raised = cm.exception.exceptions
        self.assertTrue(
            any([
                exception for exception in exceptions_raised
                if isinstance(exception, ApplicationAlreadyExistsException)
            ])
        )
