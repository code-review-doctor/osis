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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
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

from ddd.logic.learning_unit.commands import LearningUnitSearchCommand
from ddd.logic.learning_unit.dtos import LearningUnitSearchDTO
from ddd.logic.learning_unit.tests.factory.learning_unit import CourseWithOnePartim
from infrastructure.learning_unit.repository.in_memory.learning_unit import LearningUnitRepository
from infrastructure.messages_bus import message_bus_instance


class TestSearchLearningUnits(SimpleTestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        self.repo = LearningUnitRepository()

        self.course_with_partim = CourseWithOnePartim()
        self.repo.save(self.course_with_partim)

        self.cmd = LearningUnitSearchCommand(
            code_annee_values={(self.course_with_partim.code, self.course_with_partim.year)}
        )

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            LearningUnitRepository=lambda: self.repo,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)
        self.message_bus = message_bus_instance

    def test_should_retourner_liste_vide_si_aucun_criteres_donnes(self):
        cmd = attr.evolve(self.cmd, code_annee_values=set())

        result = self.message_bus.invoke(cmd)

        self.assertListEqual(result, [])

    def test_should_retourner_liste_vide_si_criteres_ne_correspond_a_aucun_partims(self):
        cmd = attr.evolve(self.cmd, code_annee_values={("LECGE2569A", 2020)})

        result = self.message_bus.invoke(cmd)

        self.assertListEqual(result, [])

    def test_should_retourner_resultats_si_criteres_corresponds(self):
        result = self.message_bus.invoke(self.cmd)

        self.assertCountEqual(
            result,
            [
                LearningUnitSearchDTO(
                    year=self.course_with_partim.year,
                    code=self.course_with_partim.code,
                    full_title=self.course_with_partim.complete_title_fr,
                    type=self.course_with_partim.type,
                    responsible_entity_code=self.course_with_partim.responsible_entity_identity.code,
                    responsible_entity_title='',
                    partims=self.course_with_partim.get_partims_information()
                )
            ]
        )

