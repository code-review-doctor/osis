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

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from base.models.enums.learning_unit_year_session import DerogationSession
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.commands import UpdateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from ddd.logic.learning_unit.domain.validator.exceptions import ShouldBeAlphanumericException, \
    AnnualVolumeInvalidException, \
    TeachingPlaceRequiredException, DerogationQuadrimesterInvalidChoiceException, \
    DerogationSessionInvalidChoiceException
from ddd.logic.learning_unit.tests.factory.effective_class import LecturingEffectiveClassFactory
from ddd.logic.learning_unit.tests.factory.learning_unit import CourseWithLecturingVolumesOnly
from ddd.logic.learning_unit.use_case.write.update_effective_class_service import update_effective_class
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository


class UpdateClassService(SimpleTestCase):
    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.ue_with_lecturing_and_practical_volumes = CourseWithLecturingVolumesOnly()
        self.learning_unit_repository.save(self.ue_with_lecturing_and_practical_volumes)

        self.effective_class_repository = EffectiveClassRepository()
        class_code = 'A'
        self.existing_class = LecturingEffectiveClassFactory(
            entity_id__class_code=class_code,
            entity_id__learning_unit_identity=self.ue_with_lecturing_and_practical_volumes.entity_id,
        )
        self.effective_class_repository.save(self.existing_class)

        self.update_class_cmd = UpdateEffectiveClassCommand(
            class_code=class_code,
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

    def test_should_class_exists(self):
        inexisting_class_code = "W"
        cmd = attr.evolve(
            self.update_class_cmd,
            class_code=inexisting_class_code,
        )
        with self.assertRaises(AttributeError) as none_type:
            update_effective_class(cmd, self.learning_unit_repository, self.effective_class_repository)
            self.assertEqual(str(none_type.exception), "'NoneType' object has no attribute 'update'")

    def test_should_class_volumes_be_consistent_with_learning_unit_when_q1_and_q2_are_filled(self):
        annual_volume = self.ue_with_lecturing_and_practical_volumes.lecturing_part.volumes.volume_annual
        bad_repartition = annual_volume + 10.0
        cmd = attr.evolve(
            self.update_class_cmd,
            volume_first_quadrimester=bad_repartition,
            volume_second_quadrimester=bad_repartition,
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            update_effective_class(cmd, self.learning_unit_repository, self.effective_class_repository)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            AnnualVolumeInvalidException
        )

    def test_should_class_volumes_be_consistent_with_learning_unit_when_only_q2_is_null(self):
        annual_volume = self.ue_with_lecturing_and_practical_volumes.lecturing_part.volumes.volume_annual
        cmd = attr.evolve(
            self.update_class_cmd,
            volume_first_quadrimester=annual_volume - 1,
            volume_second_quadrimester=None,
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            update_effective_class(cmd, self.learning_unit_repository, self.effective_class_repository)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            AnnualVolumeInvalidException
        )

    def test_should_class_volumes_be_consistent_with_learning_unit_when_only_q1_is_null(self):
        annual_volume = self.ue_with_lecturing_and_practical_volumes.lecturing_part.volumes.volume_annual
        cmd = attr.evolve(
            self.update_class_cmd,
            volume_first_quadrimester=None,
            volume_second_quadrimester=annual_volume - 1,
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            update_effective_class(cmd, self.learning_unit_repository, self.effective_class_repository)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            AnnualVolumeInvalidException
        )

    def test_should_ignore_volumes_consistency_when_no_volumes_encoded(self):
        cmd = attr.evolve(
            self.update_class_cmd,
            volume_first_quadrimester=0.0,
            volume_second_quadrimester=0.0,
        )
        self.assertTrue(
            update_effective_class(
                cmd,
                self.learning_unit_repository,
                self.effective_class_repository
            )
        )

    def test_should_teaching_place_be_required(self):
        cmd = attr.evolve(
            self.update_class_cmd,
            teaching_place_uuid=None
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            update_effective_class(cmd, self.learning_unit_repository, self.effective_class_repository)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            TeachingPlaceRequiredException
        )

    def test_should_quadrimester_be_valid_choice(self):
        cmd = attr.evolve(
            self.update_class_cmd,
            derogation_quadrimester="invalid choice",
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            update_effective_class(cmd, self.learning_unit_repository, self.effective_class_repository)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            DerogationQuadrimesterInvalidChoiceException
        )

    def test_should_session_be_valid_choice(self):
        cmd = attr.evolve(
            self.update_class_cmd,
            session_derogation="invalid choice",
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            update_effective_class(cmd, self.learning_unit_repository, self.effective_class_repository)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            DerogationSessionInvalidChoiceException
        )

    def test_should_session_be_valid_choice(self):
        cmd = attr.evolve(
            self.update_class_cmd,
            session_derogation="invalid choice",
        )
        with self.assertRaises(MultipleBusinessExceptions) as class_exceptions:
            update_effective_class(cmd, self.learning_unit_repository, self.effective_class_repository)
        self.assertIsInstance(
            class_exceptions.exception.exceptions.pop(),
            DerogationSessionInvalidChoiceException
        )
