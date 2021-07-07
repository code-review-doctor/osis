from decimal import Decimal
from unittest.mock import patch

import attr
from django.test import SimpleTestCase

from ddd.logic.effective_class_repartition.commands import SearchTutorsDistributedToClassCommand
from ddd.logic.effective_class_repartition.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.effective_class_repartition.tests.factory.tutor import Tutor9999IdentityFactory, \
    TutorWithDistributedEffectiveClassesFactory
from ddd.logic.effective_class_repartition.use_case.read.search_effective_classes_distributed_service import \
    search_tutors_distributed_to_class
from ddd.logic.learning_unit.tests.factory.learning_unit import LDROI1001LearningUnitIdentityFactory
from infrastructure.effective_class_repartition.domain.service.in_memory.tutor_attribution import \
    TutorAttributionToLearningUnitTranslator
from infrastructure.effective_class_repartition.repository.in_memory.tutor import TutorRepository


class TestSearchEffectiClassesDistributedService(SimpleTestCase):

    def setUp(self):
        # tutor_id = Tutor9999IdentityFactory()
        # self.learning_unit_id = tutor.distributed_effective_classes[0].effective_class.learning_unit_identity
        # self.command = SearchTutorsDistributedToClassCommand(
        #     learning_unit_code="LDROI1001",
        #     learning_unit_year=2020,
        #     class_code="X",
        # )
        self.service = search_tutors_distributed_to_class
        self.tutor_repository = TutorRepository()
        self.translator = TutorAttributionToLearningUnitTranslator()

    @patch("infrastructure.attribution.domain.service.tutor_attribution.TutorAttributionToLearningUnitTranslator")
    def test_should_correctly_aggregate_data(self, mock_translator):
        tutor_id = Tutor9999IdentityFactory()
        tutor = TutorWithDistributedEffectiveClassesFactory(entity_id=tutor_id)
        self.tutor_repository.save(tutor)
        distributed_class = tutor.distributed_effective_classes[0]
        effective_class_id = distributed_class.effective_class
        learning_unit_id = effective_class_id.learning_unit_identity
        mock_translator.return_value = TutorAttributionToLearningUnitDTO(
            # learning_unit_code=learning_unit_id.code,
            # learning_unit_year=learning_unit_id.year,
            attribution_uuid=distributed_class.attribution.uuid,
            last_name="Smith",
            first_name="Charles",
            personal_id_number=tutor_id.personal_id_number,
            function="FUNCTION",
            attributed_volume_to_learning_unit=Decimal(10.0),
        )
        command = SearchTutorsDistributedToClassCommand(
            learning_unit_code=learning_unit_id.code,
            learning_unit_year=learning_unit_id.year,
            class_code=effective_class_id.class_code,
        )
        result = search_tutors_distributed_to_class(command, self.translator, self.tutor_repository)

        self.assertTrue(len(result) == 1)
        first_dto = result[0]
        self.assertEqual(first_dto.attribution_uuid, "165-656849465ezd")
        self.assertEqual(first_dto.last_name, "Smith")
        self.assertEqual(first_dto.first_name, "Charles")
        self.assertEqual(first_dto.function, "FUNCTION")
        self.assertEqual(
            first_dto.distributed_volume_to_class,
            distributed_class.distributed_volume
        )
