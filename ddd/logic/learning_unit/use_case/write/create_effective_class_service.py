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

from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.commands import CreateEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from ddd.logic.learning_unit.domain.service.create_effective_class import CreateEffectiveClass
from ddd.logic.learning_unit.repository.i_effective_class import IEffectiveClassRepository
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository


@transaction.atomic()
def create_effective_class(
        cmd: 'CreateEffectiveClassCommand',
        learning_unit_repository: 'ILearningUnitRepository',
        class_repository: 'IEffectiveClassRepository'

) -> 'EffectiveClassIdentity':
    # Given
    learning_unit = learning_unit_repository.get(
        entity_id=LearningUnitIdentityBuilder.build_from_code_and_year(cmd.learning_unit_code, cmd.year)
    )
    all_existing_class_identities = class_repository.get_all_identities()

    # When
    effective_class = CreateEffectiveClass().create(
        cmd=cmd,
        learning_unit_repository=learning_unit_repository,
        all_existing_class_identities=all_existing_class_identities,
        learning_unit=learning_unit
    )

    # Then
    class_repository.save(effective_class)
    return effective_class.entity_id
