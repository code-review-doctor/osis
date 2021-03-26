from typing import List

from django.db import transaction

from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity, LearningUnit
from workshops_ddd_ue.dto.learning_unit_dto import LearningUnitDataDTO
from workshops_ddd_ue.factory.learning_unit_factory import LearningUnitBuilder
from workshops_ddd_ue.factory.responsible_entity_identity_factory import ResponsibleEntityIdentityBuilder
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
    cmd.should_be_valid()
    dto = LearningUnitDataDTO(**cmd.__dict__)

    # WHEN
    learning_unit = LearningUnitBuilder.build(dto, all_existing_identities)

    # THEN
    repository.create(learning_unit)

    return learning_unit.entity_id
