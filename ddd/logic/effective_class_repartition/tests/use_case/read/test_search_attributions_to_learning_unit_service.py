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
import datetime
from unittest import mock

import attr
from django.test import SimpleTestCase

from attribution.models.enums.function import Functions
from ddd.logic.effective_class_repartition.commands import SearchAttributionsToLearningUnitCommand
from infrastructure.effective_class_repartition.domain.service.in_memory.tutor_attribution import \
    TutorAttributionToLearningUnitTranslatorInMemory
from infrastructure.effective_class_repartition.repository.in_memory.tutor import TutorRepository as \
    TutorRepositoryInMemory
from infrastructure.messages_bus import message_bus_instance


class SearchAttributionsToLearningUnitTest(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = datetime.date.today().year
        self.matricule_enseignant = '00321234'
        self.code_unite_enseignement = 'LDROI1001'

        self.cmd = SearchAttributionsToLearningUnitCommand(
            learning_unit_code=self.code_unite_enseignement,
            learning_unit_year=self.annee,
        )

        self.attributions_translator = TutorAttributionToLearningUnitTranslatorInMemory()
        self.tutor_repository = TutorRepositoryInMemory()

        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            TutorAttributionToLearningUnitTranslator=lambda: self.attributions_translator,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_should_renvoyer_aucun_resultat(self):
        cmd = attr.evolve(self.cmd, learning_unit_code='Inexistant')
        result = self.message_bus.invoke(cmd)
        self.assertEqual(result, list())

    def test_should_renvoyer_details_attribution_enseignant(self):
        result = self.message_bus.invoke(self.cmd)
        dto = result[0]
        self.assertEqual(dto.attribution_uuid, 'attribution_uuid1')
        self.assertEqual(dto.personal_id_number, self.matricule_enseignant)
        self.assertEqual(dto.function, Functions.COORDINATOR.name)
        self.assertEqual(dto.last_name, "Smith")
        self.assertEqual(dto.first_name, "Charles")

    def test_should_renvoyer_unite_enseignement(self):
        result = self.message_bus.invoke(self.cmd)
        dto = result[0]
        self.assertEqual(dto.learning_unit_code, self.code_unite_enseignement)
        self.assertEqual(dto.learning_unit_year, self.annee)

    def test_should_renvoyer_volumes_magistraux_et_pratiques(self):
        result = self.message_bus.invoke(self.cmd)
        dto = result[0]
        self.assertEqual(dto.lecturing_volume_attributed, 10.0)
        self.assertEqual(dto.practical_volume_attributed, 15.0)
