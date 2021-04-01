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

from ddd.logic.learning_unit.builder.responsible_entity_identity_builder import ResponsibleEntityIdentityBuilder
from ddd.logic.learning_unit.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain.learning_unit import LearningUnitIdentity
from ddd.logic.learning_unit.domain.service.create_learning_unit import CreateLearningUnit
from infrastructure.learning_unit.repository.entity_repository import EntityRepository
from infrastructure.learning_unit.repository.learning_unit import LearningUnitRepository


@transaction.atomic()
def create_learning_unit(cmd: CreateLearningUnitCommand) -> LearningUnitIdentity:
    # GIVEN
    repository = LearningUnitRepository()
    all_existing_identities = repository.get_identities()
    entity = EntityRepository.get(
        entity_id=ResponsibleEntityIdentityBuilder.build_from_code(cmd.responsible_entity_code),
    )

    # WHEN
    learning_unit = CreateLearningUnit.create(entity, cmd, all_existing_identities)

    # THEN
    repository.save(learning_unit)

    return learning_unit.entity_id
