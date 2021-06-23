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
from ddd.logic.learning_unit.domain.service.effective_class_can_be_deleted import EffectiveClassCanBeDeleted

from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository


def check_can_delete_effective_class(
        cmd: 'CanDeleteEffectiveClassCommand',
        effective_class_repository: 'IEffectiveClassRepository',
        learning_unit_repository: 'ILearningUnitRepository'
) -> None:
    effective_class_identity = EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
        class_code=cmd.class_code,
        learning_unit_code=cmd.learning_unit_code,
        learning_unit_year=cmd.year
    )
    effective_class = effective_class_repository.get(entity_id=effective_class_identity)

    learning_unit_identity = LearningUnitIdentityBuilder.build_from_code_and_year(
        code=cmd.learning_unit_code,
        year=cmd.year
    )
    learning_unit = learning_unit_repository.get(learning_unit_identity)

    EffectiveClassCanBeDeleted().verify(
        effective_class=effective_class,
        learning_unit=learning_unit,
        learning_unit_repository=learning_unit_repository,
    )

