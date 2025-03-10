##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

import attr
import mock
from django.test import SimpleTestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.learning_unit_year_session import DerogationSession
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import LecturingEffectiveClass, PracticalEffectiveClass
from ddd.logic.learning_unit.domain.validator.exceptions import ShouldBeAlphanumericException, \
    CodeClassAlreadyExistForUeException, ClassTypeInvalidException, AnnualVolumeInvalidException, \
    LearningUnitHasPartimException, LearningUnitHasProposalException, LearningUnitHasEnrollmentException, \
    LearningUnitHasNoVolumeException, TeachingPlaceRequiredException, DerogationQuadrimesterInvalidChoiceException, \
    DerogationSessionInvalidChoiceException, LearningUnitNotExistingException
from ddd.logic.learning_unit.tests.factory.learning_unit import CourseWithPracticalVolumesOnly, \
    CourseWithLecturingVolumesOnly, CourseWithLecturingAndPracticalVolumes, \
    LDROI1002ExternalLearningUnitFactory, CourseWithOnePartim, LDROI1004CourseWithoutVolumesLearningUnitFactory
from ddd.logic.learning_unit.use_case.write.create_effective_class_service import create_effective_class
from infrastructure.learning_unit.domain.service.in_memory.student_enrollments_to_effective_class import \
    StudentEnrollmentsTranslatorInMemory
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository


class CreateEffectiveClassService(SimpleTestCase):
    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.learning_unit_repository.reset()
        self.ue_with_lecturing_and_practical_volumes = CourseWithLecturingAndPracticalVolumes()
        self.learning_unit_repository.save(self.ue_with_lecturing_and_practical_volumes)
        self.student_enrollment_translator = StudentEnrollmentsTranslatorInMemory()

        self.effective_class_repository = EffectiveClassRepository()
        self.effective_class_repository.reset()

        self.create_class_cmd = CreateEffectiveClassCommand(
            class_code="A",
            learning_unit_code=self.ue_with_lecturing_and_practical_volumes.code,
            year=self.ue_with_lecturing_and_practical_volumes.year,
            volume_first_quadrimester=15.0,
            volume_second_quadrimester=5.0,
            title_fr='Fr',
            title_en='en',
            derogation_quadrimester='Q1',
            session_derogation=DerogationSession.DEROGATION_SESSION_123.value,
            teaching_place_uuid="35bbb236-7de6-4322-a496-fa8397054305"
        )

    def test_should_save_type_practical(self):
        ue_with_practical_volumes_only = CourseWithPracticalVolumesOnly()
        self.learning_unit_repository.save(ue_with_practical_volumes_only)

        cmd = attr.evolve(
            self.create_class_cmd,
            year=ue_with_practical_volumes_only.year,
            learning_unit_code=ue_with_practical_volumes_only.code,
        )
        effective_class_id = create_effective_class(
            cmd,
            self.learning_unit_repository,
            self.effective_class_repository,
            self.student_enrollment_translator
        )
        effective_class = self.effective_class_repository.get(effective_class_id)
        self.assertIsInstance(effective_class, PracticalEffectiveClass)

    def test_should_save_type_lecturing(self):
        ue_with_lecturing_volumes_only = CourseWithLecturingVolumesOnly()
        self.learning_unit_repository.save(ue_with_lecturing_volumes_only)

        cmd = attr.evolve(
            self.create_class_cmd,
            year=ue_with_lecturing_volumes_only.year,
            learning_unit_code=ue_with_lecturing_volumes_only.code,
        )
        effective_class_id = create_effective_class(
            cmd,
            self.learning_unit_repository,
            self.effective_class_repository,
            self.student_enrollment_translator
        )
        effective_class = self.effective_class_repository.get(effective_class_id)
        self.assertIsInstance(effective_class, LecturingEffectiveClass)

    def test_should_save_type_lecturing_when_both_volumes_are_filled(self):
        ue_with_lecturing_and_practical_volumes = CourseWithLecturingAndPracticalVolumes()
        self.learning_unit_repository.save(ue_with_lecturing_and_practical_volumes)

        cmd = attr.evolve(
            self.create_class_cmd,
            year=ue_with_lecturing_and_practical_volumes.year,
            learning_unit_code=ue_with_lecturing_and_practical_volumes.code,
        )
        effective_class_id = create_effective_class(
            cmd,
            self.learning_unit_repository,
            self.effective_class_repository,
            self.student_enrollment_translator
        )
        effective_class = self.effective_class_repository.get(effective_class_id)
        self.assertIsInstance(effective_class, LecturingEffectiveClass)

    def test_should_class_code_be_alphanumeric(self):
        cmd = attr.evolve(
            self.create_class_cmd,
            class_code='*',
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            ShouldBeAlphanumericException
        )

    def test_should_class_code_be_unique_for_ue(self):
        cmd = attr.evolve(
            self.create_class_cmd,
            class_code="B",
        )
        # Creates the class
        create_effective_class(
            cmd,
            self.learning_unit_repository,
            self.effective_class_repository,
            self.student_enrollment_translator
        )

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            # Trying to create the same class a second time
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            CodeClassAlreadyExistForUeException
        )

    def test_should_not_be_type_mobility_or_external(self):
        ue_external = LDROI1002ExternalLearningUnitFactory()
        self.learning_unit_repository.save(ue_external)

        cmd = attr.evolve(
            self.create_class_cmd,
            learning_unit_code=ue_external.code,
            year=ue_external.year,
            class_code="A",
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            ClassTypeInvalidException
        )

    @mock.patch(
        'infrastructure.learning_unit.repository.in_memory.learning_unit.LearningUnitRepository.'
        'has_proposal_this_year_or_in_past',
        return_value=True
    )
    def test_should_learning_unit_not_have_proposal(self, mock_proposal):
        cmd = attr.evolve(
            self.create_class_cmd,
            class_code="Z",
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            LearningUnitHasProposalException
        )

    def test_should_learning_unit_not_have_enrollment(self):
        cmd = attr.evolve(
            self.create_class_cmd,
            class_code="Z",
        )
        student_enrollment_translator = StudentEnrollmentsTranslatorInMemory()
        student_enrollment_translator.has_enrollments_to_learning_unit = lambda *args: True
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            LearningUnitHasEnrollmentException
        )

    def test_should_learning_unit_not_have_partim(self):
        ue_with_one_partim = CourseWithOnePartim()
        self.learning_unit_repository.save(ue_with_one_partim)

        cmd = attr.evolve(
            self.create_class_cmd,
            learning_unit_code=ue_with_one_partim.code,
            year=ue_with_one_partim.year,
            class_code="B",
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            LearningUnitHasPartimException
        )

    def test_should_learning_unit_have_volumes(self):
        ue_without_volumes = LDROI1004CourseWithoutVolumesLearningUnitFactory(partims=[])
        self.learning_unit_repository.save(ue_without_volumes)

        cmd = attr.evolve(
            self.create_class_cmd,
            learning_unit_code=ue_without_volumes.code,
            year=ue_without_volumes.year,
            class_code="B",
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            LearningUnitHasNoVolumeException
        )

    def test_should_class_volumes_be_consistent_with_learning_unit(self):
        annual_volume = self.ue_with_lecturing_and_practical_volumes.lecturing_part.volumes.volume_annual
        bad_repartition = annual_volume + 10.0
        cmd = attr.evolve(
            self.create_class_cmd,
            class_code="C",
            volume_first_quadrimester=bad_repartition,
            volume_second_quadrimester=bad_repartition,
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            AnnualVolumeInvalidException
        )

    def test_should_ignore_volumes_consistency_when_no_volumes_encoded(self):
        cmd = attr.evolve(
            self.create_class_cmd,
            class_code="D",
            volume_first_quadrimester=0.0,
            volume_second_quadrimester=0.0,
        )
        self.assertTrue(
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        )

    def test_should_teaching_place_be_required(self):
        cmd = attr.evolve(
            self.create_class_cmd,
            class_code="B",
            teaching_place_uuid=None
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            TeachingPlaceRequiredException
        )

    def test_should_quadrimester_be_valid_choice(self):
        cmd = attr.evolve(
            self.create_class_cmd,
            class_code="B",
            derogation_quadrimester="invalid choice",
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            DerogationQuadrimesterInvalidChoiceException
        )

    def test_should_session_be_valid_choice(self):
        cmd = attr.evolve(
            self.create_class_cmd,
            class_code="B",
            session_derogation="invalid choice",
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            DerogationSessionInvalidChoiceException
        )

    def test_should_learning_unit_year_exists(self):
        cmd = attr.evolve(
            self.create_class_cmd,
            class_code="A",
            year=self.ue_with_lecturing_and_practical_volumes.year+1
        )

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            # Trying to create the same class a second time
            create_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository,
                self.student_enrollment_translator
            )
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            LearningUnitNotExistingException
        )
