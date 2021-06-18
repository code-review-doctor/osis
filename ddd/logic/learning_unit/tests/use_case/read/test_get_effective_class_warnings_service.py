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

from ddd.logic.learning_unit.commands import GetEffectiveClassWarningsCommand
from ddd.logic.learning_unit.domain.model._volumes_repartition import ClassVolumes
from ddd.logic.learning_unit.tests.factory.effective_class import SelfConsistentLecturingEffectiveClassFactory
from ddd.logic.learning_unit.tests.factory.learning_unit import LDROI1001CourseLearningUnitFactory
from ddd.logic.learning_unit.use_case.read.get_effective_class_warnings_service import get_effective_class_warnings
from infrastructure.learning_unit.repository.in_memory.effective_class import EffectiveClassRepository
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository


class TestGetEffectiveClassWarningsService(TestCase):

    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.effective_class_repository = EffectiveClassRepository()

        self.learning_unit = LDROI1001CourseLearningUnitFactory()
        self.learning_unit_repository.save(self.learning_unit)

    def test_should_get_no_warning(self):
        effective_class = SelfConsistentLecturingEffectiveClassFactory(
            entity_id__learning_unit_identity=self.learning_unit.entity_id,
            volumes=ClassVolumes(
                volume_first_quadrimester=self.learning_unit.lecturing_part.volumes.volume_first_quadrimester,
                volume_second_quadrimester=self.learning_unit.lecturing_part.volumes.volume_second_quadrimester,
            ),
            derogation_quadrimester=self.learning_unit.derogation_quadrimester.name,
            session_derogation=self.learning_unit.derogation_session.value
        )
        self.effective_class_repository.save(effective_class)

        cmd = GetEffectiveClassWarningsCommand(
            class_code=effective_class.class_code,
            learning_unit_year=self.learning_unit.year,
            learning_unit_code=self.learning_unit.code,
        )
        warnings = get_effective_class_warnings(
            cmd=cmd,
            effective_class_repository=self.effective_class_repository,
            learning_unit_repository=self.learning_unit_repository
        )
        self.assertFalse(warnings)

    def test_should_get_only_volume_warning(self):
        pass

    def test_should_get_only_quadrimester_warning(self):
        pass

    def test_should_get_only_session_warning(self):
        pass
