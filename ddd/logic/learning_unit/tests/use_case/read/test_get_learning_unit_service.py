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

from ddd.logic.learning_unit.commands import GetLearningUnitCommand
from ddd.logic.learning_unit.tests.factory.learning_unit import LDROI1001CourseLearningUnitFactory
from ddd.logic.learning_unit.use_case.read import get_learning_unit_service
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository


class TestGetLearningUnitService(SimpleTestCase):

    def setUp(self):
        self.learning_unit_repository = LearningUnitRepository()
        self.learning_unit = LDROI1001CourseLearningUnitFactory()
        self.learning_unit_repository.save(self.learning_unit)
        self.command = GetLearningUnitCommand(code=self.learning_unit.code, year=self.learning_unit.year)

    def test_get_correct_learning_unit(self):
        learning_unit = get_learning_unit_service.get_learning_unit(
            self.command,
            self.learning_unit_repository,
        )
        self.assertEqual(learning_unit, self.learning_unit)
        fields = vars(self.learning_unit)
        for field in fields:
            self.assertEqual(getattr(learning_unit, field), getattr(self.learning_unit, field), field)
