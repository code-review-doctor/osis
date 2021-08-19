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
from unittest import mock

from django.test import SimpleTestCase

from attribution.models.enums.function import Functions
from ddd.logic.effective_class_repartition.commands import SearchClassesEnseignantCommand
from ddd.logic.effective_class_repartition.tests.factory.tutor import TutorWithDistributedEffectiveClassesFactory, \
    _ClassVolumeRepartitionFactory
from infrastructure.effective_class_repartition.domain.service.in_memory.tutor_attribution import \
    ITutorAttributionToLearningUnitTranslatorInMemory
from infrastructure.effective_class_repartition.repository.in_memory.tutor import TutorRepository as \
    TutorRepositoryInMemory
from infrastructure.messages_bus import message_bus_instance


class SearchClassesEnseignantTest(SimpleTestCase):

    def setUp(self) -> None:
        self.annee = 2020
        self.numero_session = 2
        self.matricule_enseignant = '00321234'
        self.code_unite_enseignement = 'LDROI1001'
        self.nom_cohorte = 'DROI1BA'
        self.attribution_uuid = '4587-1988-4a83-a5bf-58a4511471a1'

        self.cmd = SearchClassesEnseignantCommand(matricule_fgs_enseignant=self.matricule_enseignant)

        self.attributions_translator = ITutorAttributionToLearningUnitTranslatorInMemory()
        self.tutor_repository = TutorRepositoryInMemory()
        self.tutor = TutorWithDistributedEffectiveClassesFactory(
            entity_id__personal_id_number=self.matricule_enseignant,
            distributed_effective_classes=[_ClassVolumeRepartitionFactory(attribution__uuid=self.attribution_uuid)]
        )
        self.tutor_repository.save(self.tutor)
        self.__mock_service_bus()

    def __mock_service_bus(self):
        message_bus_patcher = mock.patch.multiple(
            'infrastructure.messages_bus',
            TutorAttributionToLearningUnitTranslator=lambda: self.attributions_translator,
            TutorRepository=lambda: self.tutor_repository,
        )
        message_bus_patcher.start()
        self.addCleanup(message_bus_patcher.stop)

        self.message_bus = message_bus_instance

    def test_should_renvoyer_aucun_resultat(self):
        cmd = SearchClassesEnseignantCommand(matricule_fgs_enseignant="Inexistant")
        result = self.message_bus.invoke(cmd)
        self.assertEqual(result, list())

    def test_should_renvoyer_details_attribution_enseignant(self):
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(len(result), 1)
        dto = result[0]
        self.assertEqual(dto.attribution_uuid, '4587-1988-4a83-a5bf-58a4511471a1')
        self.assertEqual(dto.personal_id_number, self.matricule_enseignant)
        self.assertEqual(dto.function, Functions.COORDINATOR.name)
        self.assertEqual(dto.last_name, "Smith")
        self.assertEqual(dto.first_name, "Charles")

    def test_should_renvoyer_volume_enseignant_distribue_sur_classe(self):
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(len(result), 1)
        dto = result[0]
        self.assertEqual(
            dto.distributed_volume_to_class,
            self.tutor.distributed_effective_classes[0].distributed_volume,
        )

    def test_should_renvoyer_code_complet_classe_et_annee(self):
        result = self.message_bus.invoke(self.cmd)
        self.assertEqual(len(result), 1)
        dto = result[0]
        self.assertEqual(
            dto.complete_class_code,
            self.tutor.distributed_effective_classes[0].effective_class.complete_class_code,
        )
        self.assertEqual(
            dto.annee,
            self.tutor.distributed_effective_classes[0].effective_class.learning_unit_identity.year,
        )



