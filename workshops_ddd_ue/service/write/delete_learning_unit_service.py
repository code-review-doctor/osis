from typing import List

from django.db import transaction

from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from workshops_ddd_ue.command import DeleteLearningUnitCommand
from workshops_ddd_ue.domain._academic_year import AcademicYear
from workshops_ddd_ue.domain.learning_unit_year import LearningUnitIdentity
from workshops_ddd_ue.repository.learning_unit import LearningUnitRepository


@transaction.atomic()
def delete_learning_unit(cmd: DeleteLearningUnitCommand) -> LearningUnitIdentity:
    # GIVEN
    learning_unit = LearningUnitRepository().get(
        entity_id=LearningUnitIdentity(
            code=cmd.code,
            academic_year=AcademicYear(year=cmd.academic_year),
        )
    )

    all_programs = ProgramTreeRepository().search_from_children()

    # WHEN

    # THEN

    return learning_unit.entity_id
