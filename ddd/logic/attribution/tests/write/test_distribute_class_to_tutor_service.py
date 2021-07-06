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
import random
from decimal import Decimal

import attr
from django.test import SimpleTestCase

from base.ddd.utils.business_validator import MultipleBusinessExceptions
from ddd.logic.attribution.commands import DistributeClassToTutorCommand
from ddd.logic.attribution.domain.validator.exceptions import TutorAlreadyAssignedException
from ddd.logic.attribution.tests.factory.tutor import TutorWithoutDistributedEffectiveClassesFactory
from ddd.logic.attribution.use_case.write.distribute_class_to_tutor_service import distribute_class_to_tutor
from ddd.logic.effective_class_repartition.domain.validator.exceptions import VolumeShouldBeNumericException, \
    InvalidVolumeException
from ddd.logic.learning_unit.tests.factory.effective_class import LecturingEffectiveClassFactory
from infrastructure.attribution.repository.in_memory.tutor import TutorRepository
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository


class DistributeClassToTutorService(SimpleTestCase):
    def setUp(self):
        self.tutor_repository = TutorRepository()
        self.effective_class_repository = EffectiveClassRepository()
        self.tutor = TutorWithoutDistributedEffectiveClassesFactory()
        self.tutor_repository.save(self.tutor)
        self.effective_class = LecturingEffectiveClassFactory()
        self.effective_class_repository.save(self.effective_class)
        self.distribute_class_cmd = DistributeClassToTutorCommand(
            class_code=self.effective_class.entity_id.class_code,
            learning_unit_code=self.effective_class.entity_id.learning_unit_identity.code,
            learning_unit_attribution_uuid='uuid',
            year=self.effective_class.entity_id.learning_unit_identity.academic_year.year,
            tutor_personal_id_number=self.tutor.entity_id.personal_id_number,
            distributed_volume=self.effective_class.volumes.volume_first_quadrimester
        )

    def test_should_distribute_effective_class(self):
        tutor_id = distribute_class_to_tutor(
            self.distribute_class_cmd,
            self.tutor_repository,
            self.effective_class_repository
        )
        tutor = self.tutor_repository.get(tutor_id)
        class_volume = tutor.distributed_effective_classes[0]
        self.assertEqual(class_volume.distributed_volume, self.distribute_class_cmd.distributed_volume)
        self.assertEqual(class_volume.attribution.uuid, 'uuid')
        self.assertEqual(class_volume.effective_class, self.effective_class.entity_id)

    def test_should_have_number_or_decimal_distributed_volume(self):
        bad_volume = random.choice(['aaa', '12ab', True])
        cmd = attr.evolve(self.distribute_class_cmd, distributed_volume=bad_volume)
        with self.assertRaises(MultipleBusinessExceptions) as e:
            distribute_class_to_tutor(cmd, self.tutor_repository, self.effective_class_repository)
        self.assertIsInstance(
            e.exception.exceptions.pop(),
            VolumeShouldBeNumericException
        )

    def test_should_have_available_and_greater_than_0_distributed_volume(self):
        bad_volume = random.choice([Decimal(-5.0), self.effective_class.volumes.total_volume + 5])
        cmd = attr.evolve(self.distribute_class_cmd, distributed_volume=bad_volume)
        with self.assertRaises(MultipleBusinessExceptions) as e:
            distribute_class_to_tutor(cmd, self.tutor_repository, self.effective_class_repository)
        self.assertIsInstance(
            e.exception.exceptions.pop(),
            InvalidVolumeException
        )

    def test_should_tutor_not_be_already_assigned(self):
        distribute_class_to_tutor(
            self.distribute_class_cmd,
            self.tutor_repository,
            self.effective_class_repository
        )
        with self.assertRaises(MultipleBusinessExceptions) as e:
            distribute_class_to_tutor(
                self.distribute_class_cmd,
                self.tutor_repository,
                self.effective_class_repository
            )
        self.assertIsInstance(e.exception.exceptions.pop(), TutorAlreadyAssignedException)
