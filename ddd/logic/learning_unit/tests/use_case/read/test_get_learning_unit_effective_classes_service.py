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

from base.models.enums.learning_component_year_type import PRACTICAL_EXERCISES, LECTURING
from ddd.logic.learning_unit.commands import GetLearningUnitEffectiveClassesCommand
from ddd.logic.learning_unit.dtos import EffectiveClassFromRepositoryDTO
from ddd.logic.learning_unit.tests.factory.effective_class import LecturingEffectiveClassFactory
from ddd.logic.learning_unit.use_case.read import get_learning_unit_effective_classes_service
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository


class TestGetLearningUnitEffectiveClassesService(SimpleTestCase):

    def setUp(self):
        self.effective_class_repository = EffectiveClassRepository()
        self.effective_class = LecturingEffectiveClassFactory()
        self.effective_class_repository.save(self.effective_class)
        self.command = GetLearningUnitEffectiveClassesCommand(
            learning_unit_code=self.effective_class.learning_unit_identity.code,
            learning_unit_year=self.effective_class.learning_unit_identity.year
        )
        self.dto = EffectiveClassFromRepositoryDTO(
            class_code=self.effective_class.class_code,
            learning_unit_code=self.effective_class.learning_unit_code,
            learning_unit_year=self.effective_class.year,
            title_fr=self.effective_class.titles.fr,
            title_en=self.effective_class.titles.en,
            teaching_place_uuid=self.effective_class.teaching_place.uuid,
            derogation_quadrimester=self.effective_class.derogation_quadrimester,
            session_derogation=self.effective_class.session_derogation,
            volume_q1=self.effective_class.volumes.volume_first_quadrimester,
            volume_q2=self.effective_class.volumes.volume_second_quadrimester,
            class_type=LECTURING if self.effective_class.is_lecturing else PRACTICAL_EXERCISES,
        )

    def test_get_correct_learning_unit(self):
        effective_classes = get_learning_unit_effective_classes_service.get_learning_unit_effective_classes(
            self.command,
            self.effective_class_repository,
        )
        self.assertEqual(effective_classes, [self.dto])
        fields = vars(self.effective_class)
        for field in fields:
            self.assertEqual(getattr(effective_classes[0], field), getattr(self.effective_class, field), field)
