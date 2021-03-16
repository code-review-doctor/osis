from typing import List

from django.db import transaction

from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity, LearningUnit
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository


@transaction.atomic()
def create_and_postpone_orphan_training(cmd: CreateLearningUnitCommand) -> List['LearningUnitIdentity']:
    # GIVEN
    repository = LearningUnitRepository()

    # WHEN
    learning_unit = LearningUnit.create(cmd, repository)

    # THEN
    repository.create(learning_unit)

    return learning_unit.entity_id
