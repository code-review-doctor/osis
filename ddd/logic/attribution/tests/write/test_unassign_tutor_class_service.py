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

from django.test import SimpleTestCase

from ddd.logic.attribution.commands import UnassignTutorClassCommand
from ddd.logic.attribution.tests.factory.tutor import TutorWithDistributedEffectiveClassesFactory
from ddd.logic.attribution.use_case.write.unassign_tutor_class_service import unassign_tutor_class
from infrastructure.attribution.repository.in_memory.tutor import TutorRepository
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository


class UnassignTutorClassService(SimpleTestCase):
    def setUp(self):
        self.tutor_repository = TutorRepository()
        self.effective_class_repository = EffectiveClassRepository()
        self.tutor = TutorWithDistributedEffectiveClassesFactory()
        self.tutor_repository.save(self.tutor)
        self.unassign_class_cmd = UnassignTutorClassCommand(
            class_code=self.tutor.distributed_effective_classes[0].effective_class.class_code,
            learning_unit_attribution_uuid=self.tutor.distributed_effective_classes[0].attribution.uuid,
            tutor_personal_id_number=self.tutor.entity_id.personal_id_number,
        )

    def test_should_distribute_effective_class(self):
        unassign_tutor_class(self.unassign_class_cmd, self.tutor_repository)
        tutor = self.tutor_repository.get(self.tutor.entity_id)
        class_volume = tutor.distributed_effective_classes
        self.assertEqual(len(class_volume), 0)
