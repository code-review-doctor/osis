from typing import List

from django.db import transaction

from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from workshops_ddd_ue.command import DeleteLearningUnitCommand
from workshops_ddd_ue.domain._academic_year import AcademicYear
from workshops_ddd_ue.domain.learning_unit import LearningUnitIdentity
from workshops_ddd_ue.domain.service.learning_unit_is_contained_in_program_tree import \
    LearningUnitCanBeDeleted
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository


@transaction.atomic()
def delete_learning_unit(cmd: DeleteLearningUnitCommand) -> LearningUnitIdentity:
    # GIVEN
    repository = LearningUnitRepository()
    learning_unit = repository.get(
        entity_id=LearningUnitIdentity(
            code=cmd.code,
            academic_year=AcademicYear(year=cmd.academic_year),
        )
    )

    # WHEN
    LearningUnitCanBeDeleted().validate(learning_unit.entity_id, ProgramTreeRepository())

    # THEN
    repository.delete(learning_unit.entity_id)

    return learning_unit.entity_id
