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
from ddd.logic.effective_class_repartition.commands import EditClassVolumeRepartitionToTutorCommand
from ddd.logic.effective_class_repartition.domain.validator.exceptions import AssignedVolumeInvalidValueException
from ddd.logic.effective_class_repartition.tests.factory.tutor import TutorWithDistributedEffectiveClassesFactory
from ddd.logic.effective_class_repartition.use_case.write.edit_class_volume_repartition_to_tutor_service import \
    edit_class_volume_repartition_to_tutor
from ddd.logic.learning_unit.tests.factory.effective_class import LecturingEffectiveClassFactory
from infrastructure.effective_class_repartition.repository.in_memory.tutor import TutorRepository
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository


class EditClassVolumeRepartitionToTutorService(SimpleTestCase):
    def setUp(self):
        self.tutor_repository = TutorRepository()
        self.effective_class_repository = EffectiveClassRepository()
        self.tutor = TutorWithDistributedEffectiveClassesFactory()
        self.tutor_repository.save(self.tutor)
        self.effective_class = LecturingEffectiveClassFactory(
            entity_id=self.tutor.distributed_effective_classes[0].effective_class
        )
        self.effective_class_repository.save(self.effective_class)
        self.edit_class_volume_cmd = EditClassVolumeRepartitionToTutorCommand(
            class_code=self.effective_class.entity_id.class_code,
            learning_unit_code=self.effective_class.entity_id.learning_unit_identity.code,
            learning_unit_attribution_uuid=self.tutor.distributed_effective_classes[0].attribution.uuid,
            year=self.effective_class.entity_id.learning_unit_identity.academic_year.year,
            tutor_personal_id_number=self.tutor.entity_id.personal_id_number,
            distributed_volume=0
        )

    def test_should_edit_class_volume_repartition(self):
        tutor_id = edit_class_volume_repartition_to_tutor(
            self.edit_class_volume_cmd,
            self.tutor_repository,
            self.effective_class_repository,
        )
        tutor = self.tutor_repository.get(tutor_id)
        class_volume = tutor.distributed_effective_classes[0]
        self.assertEqual(class_volume.distributed_volume, self.edit_class_volume_cmd.distributed_volume)
        self.assertEqual(class_volume.attribution.uuid, self.edit_class_volume_cmd.learning_unit_attribution_uuid)
        self.assertEqual(class_volume.effective_class, self.effective_class.entity_id)

    def test_should_have_available_and_greater_than_0_distributed_volume(self):
        bad_volume = random.choice([Decimal(-5.0), self.effective_class.volumes.total_volume + 5])
        cmd = attr.evolve(self.edit_class_volume_cmd, distributed_volume=bad_volume)
        with self.assertRaises(MultipleBusinessExceptions) as e:
            edit_class_volume_repartition_to_tutor(
                cmd,
                self.tutor_repository,
                self.effective_class_repository,
            )
        self.assertIsInstance(
            e.exception.exceptions.pop(),
            AssignedVolumeInvalidValueException
        )
