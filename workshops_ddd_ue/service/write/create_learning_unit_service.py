from typing import List

from django.db import transaction

from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity, LearningUnit
from workshops_ddd_ue.factory.learning_unit_factory import LearningUnitBuilder
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository


@transaction.atomic()
def create_learning_unit(cmd: CreateLearningUnitCommand) -> LearningUnitIdentity:
    # GIVEN
    repository = LearningUnitRepository()
    all_existing_identities = repository.get_identities()

    # WHEN
    learning_unit = LearningUnitBuilder.build_from_command(cmd, all_existing_identities)

    # THEN
    repository.create(learning_unit)

    return learning_unit.entity_id
