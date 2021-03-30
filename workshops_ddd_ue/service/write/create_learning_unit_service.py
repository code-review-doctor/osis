from typing import List

from django.db import transaction

from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain.learning_unit import LearningUnitIdentity, LearningUnit
from workshops_ddd_ue.builder.learning_unit_builder import LearningUnitBuilder
from workshops_ddd_ue.builder.responsible_entity_identity_builder import ResponsibleEntityIdentityBuilder
from workshops_ddd_ue.repository.entity_repository import EntityRepository
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository


@transaction.atomic()
def create_learning_unit(cmd: CreateLearningUnitCommand) -> LearningUnitIdentity:
    # GIVEN
    repository = LearningUnitRepository()
    all_existing_identities = repository.get_identities()
    entity = EntityRepository.get(
        entity_id=ResponsibleEntityIdentityBuilder.build_from_code(cmd.responsible_entity_code),
    )

    # WHEN
    learning_unit = LearningUnitBuilder.build_from_command(cmd, all_existing_identities, entity)

    # THEN
    repository.save(learning_unit)

    return learning_unit.entity_id
