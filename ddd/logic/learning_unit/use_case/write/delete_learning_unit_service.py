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
from django.db import transaction

from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from ddd.logic.learning_unit.command import DeleteLearningUnitCommand
from workshops_ddd_ue.domain._academic_year import AcademicYear
from workshops_ddd_ue.domain.learning_unit import LearningUnitIdentity
from ddd.logic.learning_unit.domain.service.learning_unit_is_contained_in_program_tree import \
    LearningUnitCanBeDeleted
from infrastructure.learning_unit.repository.learning_unit import LearningUnitRepository


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
