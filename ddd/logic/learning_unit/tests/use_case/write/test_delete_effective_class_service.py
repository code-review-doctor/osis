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
from django.test import SimpleTestCase
from django.utils.translation import gettext_lazy as _

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.learning_unit.commands import DeleteEffectiveClassCommand
from ddd.logic.learning_unit.domain.validator.exceptions import EffectiveClassHasTutorAssignedException, \
    LearningUnitOfEffectiveClassHasEnrollmentException
from ddd.logic.learning_unit.tests.factory.effective_class import LecturingEffectiveClassFactory
from ddd.logic.learning_unit.use_case.write.delete_effective_class_service import delete_effective_class
from infrastructure.learning_unit.domain.service.student_enrollments_to_effective_class import \
    StudentEnrollmentsTranslator
from infrastructure.learning_unit.domain.service.tutor_distributed_to_class import TutorAssignedToClassTranslator
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository


class DeleteEffectiveClassService(SimpleTestCase):
    def setUp(self):
        self.effective_class_repository = EffectiveClassRepository()
        class_code = 'A'
        self.existing_class = LecturingEffectiveClassFactory(
            entity_id__class_code=class_code,
        )
        self.effective_class_repository.save(self.existing_class)

        self.delete_class_cmd = DeleteEffectiveClassCommand(
            class_code=class_code,
            learning_unit_code=self.existing_class.learning_unit_code,
            year=self.existing_class.year
        )
        self.tutor_distributed_to_class = TutorAssignedToClassTranslator()
        self.tutor_distributed_to_class.get_first_tutor_full_name_if_exists = lambda *args: None

        self.has_enrollments_service = StudentEnrollmentsTranslator()
        self.has_enrollments_service.has_enrollments_to_class = lambda *args: False

    def test_should_class_exists(self):
        inexisting_class_code = "W"
        cmd = attr.evolve(
            self.delete_class_cmd,
            class_code=inexisting_class_code,
        )
        self.assertIsNone(
            delete_effective_class(
                cmd,
                self.effective_class_repository,
                self.tutor_distributed_to_class,
                self.has_enrollments_service,
            )
        )

    def test_should_delete_existing_class(self):
        effective_class = LecturingEffectiveClassFactory()
        self.effective_class_repository.save(effective_class)

        self.assertIn(effective_class, self.effective_class_repository.entities)
        entity_id = delete_effective_class(
            cmd=self.delete_class_cmd,
            effective_class_repository=self.effective_class_repository,
            has_assigned_tutor_service=self.tutor_distributed_to_class,
            has_enrollments_service=self.has_enrollments_service,
        )
        self.assertNotIn(self.existing_class, self.effective_class_repository.entities)

    def test_should_not_delete_if_has_enrollments_to_class(self):
        self.has_enrollments_service.has_enrollments_to_class = lambda *args: True

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            delete_effective_class(
                cmd=self.delete_class_cmd,
                effective_class_repository=self.effective_class_repository,
                has_assigned_tutor_service=self.tutor_distributed_to_class,
                has_enrollments_service=self.has_enrollments_service,
            )
        exceptions = class_exceptions.exception.exceptions.copy()
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            LearningUnitOfEffectiveClassHasEnrollmentException
        )

        self.assertEqual(list(exceptions)[0].message, _("Class of learning unit having enrollment can't be delete"))

    def test_should_not_delete_if_has_tutors_assigned(self):
        tutor_full_name = 'Martin tom'
        self.tutor_distributed_to_class.get_first_tutor_full_name_if_exists = lambda *args: tutor_full_name

        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            delete_effective_class(
                cmd=self.delete_class_cmd,
                effective_class_repository=self.effective_class_repository,
                has_assigned_tutor_service=self.tutor_distributed_to_class,
                has_enrollments_service=self.has_enrollments_service,
            )
        exceptions = class_exceptions.exception.exceptions.copy()
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            EffectiveClassHasTutorAssignedException
        )

        self.assertEqual(
            list(exceptions)[0].message,
            _("The class %(class_complete_code)s is assigned to %(tutor_full_name)s in %(year)s") % {
                'class_complete_code': "{}".format(
                    self.existing_class.complete_acronym
                ),
                'tutor_full_name': tutor_full_name,
                'year': self.existing_class.entity_id.learning_unit_identity.year,
            }
        )
