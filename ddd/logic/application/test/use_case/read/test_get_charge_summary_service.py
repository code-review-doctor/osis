import datetime
from decimal import Decimal

import mock
import uuid
from django.test import TestCase

from attribution.models.enums.function import Functions
from base.models.enums.vacant_declaration_type import VacantDeclarationType
from ddd.logic.application.commands import GetChargeSummaryCommand
from ddd.logic.application.domain.builder.applicant_identity_builder import ApplicantIdentityBuilder
from ddd.logic.application.domain.model.allocation_entity import AllocationEntity
from ddd.logic.application.domain.model.applicant import Applicant
from ddd.logic.application.domain.model.application_calendar import ApplicationCalendar, ApplicationCalendarIdentity
from ddd.logic.application.domain.model.attribution import Attribution
from ddd.logic.application.domain.model.vacant_course import VacantCourse, VacantCourseIdentity
from ddd.logic.application.dtos import LearningUnitVolumeFromServiceDTO, ChargeSummaryDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.shared_kernel.academic_year.builder.academic_year_identity_builder import AcademicYearIdentityBuilder
from infrastructure.application.repository.applicant_in_memory import ApplicantInMemoryRepository
from infrastructure.application.repository.application_calendar_in_memory import ApplicationCalendarInMemoryRepository
from infrastructure.application.repository.vacant_course_in_memory import VacantCourseInMemoryRepository
from infrastructure.messages_bus import message_bus_instance


class GetChargeSummary(TestCase):
    @classmethod
    def setUpTestData(cls):
        today = datetime.date.today()
        cls.application_calendar = ApplicationCalendar(
            entity_id=ApplicationCalendarIdentity(uuid=uuid.uuid4()),
            authorized_target_year=AcademicYearIdentityBuilder.build_from_year(year=2019),
            start_date=today - datetime.timedelta(days=5),
            end_date=today + datetime.timedelta(days=10),
        )
        cls.global_id = '123456789'
        cls.applicant = Applicant(
            entity_id=ApplicantIdentityBuilder.build_from_global_id(global_id=cls.global_id),
            first_name="Thomas",
            last_name="Durant",
            attributions=[
                Attribution(
                    course_id=LearningUnitIdentity(
                        code="LDROI1200",
                        academic_year=AcademicYearIdentityBuilder.build_from_year(year=2019)
                    ),
                    course_title='Introduction au droit',
                    function=Functions.CO_HOLDER,
                    end_year=AcademicYearIdentityBuilder.build_from_year(year=2030),
                    start_year=AcademicYearIdentityBuilder.build_from_year(year=2016),
                    lecturing_volume=Decimal(10),
                    practical_volume=Decimal(15),
                )
            ]
        )

        cls.vacant_course_ldroi1200 = VacantCourse(
            entity_id=VacantCourseIdentity(
                code='LDROI1200',
                academic_year=AcademicYearIdentityBuilder.build_from_year(year=2019)
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
        cls.vacant_course_repository = VacantCourseInMemoryRepository([cls.vacant_course_ldroi1200])
        cls.learning_unit_service_mocked = mock.Mock()
        cls.learning_unit_service_mocked.search_learning_unit_volumes_dto = mock.Mock(return_value=[
            LearningUnitVolumeFromServiceDTO(
                code='LDROI1200',
                year=2019,
                lecturing_volume_total=Decimal(50),
                practical_volume_total=Decimal(70),
            )
        ])
        cls.learning_unit_service_mocked.search_tutor_attribution_dto = mock.Mock(return_value=[])

    def setUp(self) -> None:
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            ApplicantRepository=lambda: self.applicant_repository,
            ApplicationCalendarRepository=lambda: self.application_calendar_repository,
            VacantCourseRepository=lambda: self.vacant_course_repository,
            LearningUnitTranslator=lambda: self.learning_unit_service_mocked
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_should_return_charge_summary_list_dto(self):
        cmd = GetChargeSummaryCommand(global_id=self.global_id)
        results = self.message_bus.invoke(cmd)

        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)

        self.assertIsInstance(results[0], ChargeSummaryDTO)
        self.assertEqual(results[0].code, "LDROI1200")
        self.assertEqual(results[0].year, 2019)
        self.assertEqual(results[0].title, "Introduction au droit")
        self.assertEqual(results[0].start_year, 2016)
        self.assertEqual(results[0].end_year, 2030)
        self.assertEqual(results[0].function, Functions.CO_HOLDER)
        self.assertEqual(results[0].lecturing_volume, Decimal(10))
        self.assertEqual(results[0].practical_volume, Decimal(15))
        self.assertEqual(results[0].lecturing_volume_available, Decimal(10))
        self.assertEqual(results[0].practical_volume_available, Decimal(50))
        self.assertEqual(results[0].total_lecturing_volume_course, Decimal(50))
        self.assertEqual(results[0].total_practical_volume_course, Decimal(70))
        self.assertEqual(results[0].tutors, [])
