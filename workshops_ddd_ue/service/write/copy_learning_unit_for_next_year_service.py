from typing import List

from django.db import transaction

from workshops_ddd_ue.command import CreateLearningUnitCommand, CopyLearningUnitToNextYearCommand
from workshops_ddd_ue.domain.learning_unit import LearningUnitIdentity, LearningUnit
from workshops_ddd_ue.builder.learning_unit_builder import LearningUnitBuilder
from workshops_ddd_ue.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository


@transaction.atomic()
def copy_learning_unit_to_next_year(cmd: CopyLearningUnitToNextYearCommand) -> LearningUnitIdentity:
    # GIVEN
    repository = LearningUnitRepository()
    learning_unit = repository.get(entity_id=LearningUnitIdentityBuilder.build_from_command(cmd))
    all_existing_learning_unit_identities = repository.get_identities()

    # WHEN
    learning_unit_net_year = LearningUnitBuilder.copy_to_next_year(learning_unit, all_existing_learning_unit_identities)

    # THEN
    repository.create(learning_unit_net_year)

    return learning_unit.entity_id
