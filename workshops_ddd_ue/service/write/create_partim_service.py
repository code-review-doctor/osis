from typing import List

from django.db import transaction

from workshops_ddd_ue.command import CreatePartimCommand
from workshops_ddd_ue.domain.learning_unit import LearningUnitIdentity, LearningUnit
from workshops_ddd_ue.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository


@transaction.atomic()
def create_partim(cmd: CreatePartimCommand) -> LearningUnitIdentity:
    # GIVEN
    repository = LearningUnitRepository()
    learning_unit = repository.get(
        entity_id=LearningUnitIdentityBuilder.build_from_code_and_year(cmd.learning_unit_code, cmd.learning_unit_year)
    )
    # WHEN
    learning_unit.create_partim(cmd)

    # THEN
    repository.save(learning_unit)

    return learning_unit.entity_id
