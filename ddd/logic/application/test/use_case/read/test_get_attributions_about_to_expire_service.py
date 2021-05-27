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

from attribution.models.enums.function import Functions
from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.commands import GetAttributionsAboutToExpireCommand
from ddd.logic.application.domain.model.applicant import Applicant, ApplicantIdentity
from ddd.logic.application.domain.model.application import Application, ApplicationIdentity
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar, ApplicationCalendarIdentity
from ddd.logic.application.domain.model.attribution import Attribution
from ddd.logic.application.domain.model.allocation_entity import AllocationEntity
from ddd.logic.application.domain.model.vacant_course import VacantCourseIdentity, VacantCourse
from ddd.logic.application.domain.validator.exceptions import VacantCourseApplicationManagedInTeamException, \
    ApplicationAlreadyExistsException, VolumesAskedShouldBeLowerOrEqualToVolumeAvailable, \
    VacantCourseNotAllowedDeclarationType, VacantCourseNotFound
from ddd.logic.application.dtos import AttributionAboutToExpireDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from infrastructure.application.repository.applicant_in_memory import ApplicantInMemoryRepository
from infrastructure.application.repository.application_calendar_in_memory import ApplicationCalendarInMemoryRepository
from infrastructure.application.repository.application_in_memory import ApplicationInMemoryRepository
from infrastructure.application.repository.vacant_course_in_memory import VacantCourseInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class TestGetAttributionsAboutToExpireService(TestCase):

    def setUp(self) -> None:
        today = datetime.date.today()
        self.application_calendar = ApplicationCalendar(
            entity_id=ApplicationCalendarIdentity(uuid=uuid.uuid4()),
            authorized_target_year=AcademicYearIdentityBuilder.build_from_year(year=2018),
            start_date=today - datetime.timedelta(days=5),
            end_date=today + datetime.timedelta(days=10),
        )

        self.attribution_about_to_expire = Attribution(
            course_id=LearningUnitIdentity(
                code="LDROI1200",
                academic_year=AcademicYearIdentityBuilder.build_from_year(year=2018)
            ),
            function=Functions.CO_HOLDER,
            end_year=self.application_calendar.authorized_target_year,
            start_year=AcademicYearIdentityBuilder.build_from_year(year=2016),
            lecturing_volume=Decimal(10),
            practical_volume=Decimal(15),
        )
        self.global_id = '123456789'
        self.applicant = Applicant(
            entity_id=ApplicantIdentity(global_id=self.global_id),
            first_name="Thomas",
            last_name="Durant",
            attributions=[self.attribution_about_to_expire]
        )

        self.vacant_course_ldroi1200 = VacantCourse(
            entity_id=VacantCourseIdentity(
                code='LDROI1200',
                academic_year=AcademicYearIdentityBuilder.build_from_year(year=2019)
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
        self.vacant_course_lagro1510 = VacantCourse(
            entity_id=VacantCourseIdentity(
                code='LAGRO1510',
                academic_year=AcademicYearIdentityBuilder.build_from_year(year=2019)
            ),
            lecturing_volume_available=Decimal(50),
            lecturing_volume_total=Decimal(50),
            practical_volume_available=Decimal(25),
            practical_volume_total=Decimal(25),
            title='Introduction en agro',
            vacant_declaration_type=VacantDeclarationType.RESEVED_FOR_INTERNS,
            is_in_team=False,
            allocation_entity=AllocationEntity(code='AGRO')
        )

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

    def test_assert_unavailable_renewal_reason_case_no_corresponding_vacant_course_next_year(self):
        self.applicant.attributions = [Attribution(
            course_id=LearningUnitIdentity(
                code="LAGRO1200",
                academic_year=AcademicYearIdentityBuilder.build_from_year(year=2020)
            ),
            function=Functions.CO_HOLDER,
            end_year=self.application_calendar.authorized_target_year,
            start_year=AcademicYearIdentityBuilder.build_from_year(year=2016),
            lecturing_volume=Decimal(10),
            practical_volume=Decimal(15),
        )]

        cmd = GetAttributionsAboutToExpireCommand(global_id=self.global_id)
        results = self.message_bus.invoke(cmd)

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], AttributionAboutToExpireDTO)
        self.assertFalse(results[0].is_renewable)
        self.assertEqual(results[0].unavailable_renewal_reason, VacantCourseNotFound().message)

        self.assertEqual(results[0].code, "LAGRO1200")
        self.assertEqual(results[0].year, 2020)
        self.assertEqual(results[0].lecturing_volume, Decimal(10))
        self.assertEqual(results[0].practical_volume, Decimal(15))
        self.assertEqual(results[0].function, Functions.CO_HOLDER)
        self.assertEqual(results[0].end_year, self.application_calendar.authorized_target_year.year)
        self.assertEqual(results[0].start_year, 2016)
        self.assertIsNone(results[0].title)
        self.assertIsNone(results[0].total_lecturing_volume_course)
        self.assertIsNone(results[0].total_practical_volume_course)
        self.assertIsNone(results[0].lecturing_volume_available)
        self.assertIsNone(results[0].practical_volume_available)

    def test_assert_unavailable_renewal_reason_case_vacant_course_next_year_organized_in_team(self):
        self.vacant_course_ldroi1200.is_in_team = True

        cmd = GetAttributionsAboutToExpireCommand(global_id=self.global_id)
        results = self.message_bus.invoke(cmd)

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], AttributionAboutToExpireDTO)
        self.assertFalse(results[0].is_renewable)
        self.assertEqual(results[0].unavailable_renewal_reason, VacantCourseApplicationManagedInTeamException().message)

    def test_assert_unavailable_renewal_reason_case_have_already_applied_on_vacant_course_next_year(self):
        self.application_repository = ApplicationInMemoryRepository([
            Application(
                entity_id=ApplicationIdentity(uuid=uuid.uuid4()),
                applicant_id=self.applicant.entity_id,
                vacant_course_id=self.vacant_course_ldroi1200.entity_id,
                lecturing_volume=Decimal(5),
                practical_volume=None,
                remark='',
                course_summary='',
            )
        ])

        cmd = GetAttributionsAboutToExpireCommand(global_id=self.global_id)
        results = self.message_bus.invoke(cmd)

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], AttributionAboutToExpireDTO)
        self.assertFalse(results[0].is_renewable)
        self.assertEqual(results[0].unavailable_renewal_reason, ApplicationAlreadyExistsException().message)

    def test_assert_unavailable_renewal_reason_case_volume_on_vacant_course_next_year_lower_than_asked(self):
        self.vacant_course_ldroi1200.lecturing_volume_available = \
            self.attribution_about_to_expire.lecturing_volume - Decimal(2)

        cmd = GetAttributionsAboutToExpireCommand(global_id=self.global_id)
        results = self.message_bus.invoke(cmd)

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], AttributionAboutToExpireDTO)
        self.assertFalse(results[0].is_renewable)
        self.assertEqual(
            results[0].unavailable_renewal_reason,
            VolumesAskedShouldBeLowerOrEqualToVolumeAvailable().message
        )

    def test_assert_unavailable_renewal_reason_case_declaration_type_disallowed(self):
        self.vacant_course_ldroi1200.vacant_declaration_type = VacantDeclarationType.VACANT_NOT_PUBLISH.name

        cmd = GetAttributionsAboutToExpireCommand(global_id=self.global_id)
        results = self.message_bus.invoke(cmd)

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], AttributionAboutToExpireDTO)
        self.assertFalse(results[0].is_renewable)
        self.assertEqual(
            results[0].unavailable_renewal_reason,
            VacantCourseNotAllowedDeclarationType().message
        )

    def test_assert_renewal_because_no_unavailable_renewal_reason(self):
        cmd = GetAttributionsAboutToExpireCommand(global_id=self.global_id)
        results = self.message_bus.invoke(cmd)

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], AttributionAboutToExpireDTO)
        self.assertTrue(results[0].is_renewable)
        self.assertIsNone(results[0].unavailable_renewal_reason)
