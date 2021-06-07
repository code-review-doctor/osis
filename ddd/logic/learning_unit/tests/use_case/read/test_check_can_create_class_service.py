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

from django.test import TestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.learning_unit.commands import CanCreateEffectiveClassCommand
from ddd.logic.learning_unit.domain.validator.exceptions import ClassTypeInvalidException, \
    LearningUnitHasPartimException, LearningUnitHasNoVolumeException, LearningUnitHasEnrollmentException, \
    LearningUnitHasProposalException
from ddd.logic.learning_unit.tests.factory.learning_unit import LDROI1002ExternalLearningUnitFactory, \
    LDROI1001CourseLearningUnitFactory, LDROI1003CourseWithPartimsLearningUnitFactory, \
    LDROI1004CourseWithoutVolumesLearningUnitFactory
from ddd.logic.learning_unit.use_case.read.check_can_create_class_service import check_can_create_effective_class
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository


class TestCheckCanCreateEffectiveClass(TestCase):

    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()

    def test_check_can_create_effective_class(self):
        LDROI1001_course = LDROI1001CourseLearningUnitFactory()
        self.learning_unit_repository.save(LDROI1001_course)

        self.cmd = CanCreateEffectiveClassCommand(
            learning_unit_code=LDROI1001_course.entity_id.code,
            learning_unit_year=LDROI1001_course.entity_id.academic_year.year
        )

        self.assertIsNone(check_can_create_effective_class(self.cmd, self.learning_unit_repository))

    def test_check_cannot_create_effective_class_invalid_learning_unit_type(self):
        LDROI1002_external = LDROI1002ExternalLearningUnitFactory()
        self.learning_unit_repository.save(LDROI1002_external)

        self.cmd = CanCreateEffectiveClassCommand(
            learning_unit_code=LDROI1002_external.entity_id.code,
            learning_unit_year=LDROI1002_external.entity_id.academic_year.year
        )

        with self.assertRaises(MultipleBusinessExceptions) as context:
            check_can_create_effective_class(self.cmd, self.learning_unit_repository)
        raised_exceptions = [type(e) for e in context.exception.exceptions]
        self.assertIn(ClassTypeInvalidException, raised_exceptions)

    def test_check_cannot_create_effective_class_for_lu_with_partims(self):

        LDROI1003_course_with_partims = LDROI1003CourseWithPartimsLearningUnitFactory()
        self.learning_unit_repository.save(LDROI1003_course_with_partims)

        self.cmd = CanCreateEffectiveClassCommand(
            learning_unit_code=LDROI1003_course_with_partims.entity_id.code,
            learning_unit_year=LDROI1003_course_with_partims.entity_id.academic_year.year
        )

        with self.assertRaises(MultipleBusinessExceptions) as context:
            check_can_create_effective_class(self.cmd, self.learning_unit_repository)
        raised_exceptions = [type(e) for e in context.exception.exceptions]
        self.assertIn(LearningUnitHasPartimException, raised_exceptions)

    def test_check_cannot_create_effective_class_for_lu_without_volumes(self):
        LDROI1004_course_without_volumes = LDROI1004CourseWithoutVolumesLearningUnitFactory()
        self.learning_unit_repository.save(LDROI1004_course_without_volumes)

        self.cmd = CanCreateEffectiveClassCommand(
            learning_unit_code=LDROI1004_course_without_volumes.entity_id.code,
            learning_unit_year=LDROI1004_course_without_volumes.entity_id.academic_year.year
        )

        with self.assertRaises(MultipleBusinessExceptions) as context:
            check_can_create_effective_class(self.cmd, self.learning_unit_repository)
        raised_exceptions = [type(e) for e in context.exception.exceptions]
        self.assertIn(LearningUnitHasNoVolumeException, raised_exceptions)

    def test_check_cannot_create_effective_class_for_lu_with_enrollments(self):
        self.learning_unit_repository.has_enrollments = lambda *args, **kwargs: True

        LDROI1001_course = LDROI1001CourseLearningUnitFactory()
        self.learning_unit_repository.save(LDROI1001_course)

        self.cmd = CanCreateEffectiveClassCommand(
            learning_unit_code=LDROI1001_course.entity_id.code,
            learning_unit_year=LDROI1001_course.entity_id.academic_year.year
        )

        with self.assertRaises(MultipleBusinessExceptions) as context:
            check_can_create_effective_class(self.cmd, self.learning_unit_repository)
        raised_exceptions = [type(e) for e in context.exception.exceptions]
        self.assertIn(LearningUnitHasEnrollmentException, raised_exceptions)

    def test_check_cannot_create_effective_class_for_lu_with_proposal(self):
        self.learning_unit_repository.has_proposal = lambda *args, **kwargs: True

        LDROI1001_course = LDROI1001CourseLearningUnitFactory()
        self.learning_unit_repository.save(LDROI1001_course)

        self.cmd = CanCreateEffectiveClassCommand(
            learning_unit_code=LDROI1001_course.entity_id.code,
            learning_unit_year=LDROI1001_course.entity_id.academic_year.year
        )

        with self.assertRaises(MultipleBusinessExceptions) as context:
            check_can_create_effective_class(self.cmd, self.learning_unit_repository)
        raised_exceptions = [type(e) for e in context.exception.exceptions]
        self.assertIn(LearningUnitHasProposalException, raised_exceptions)