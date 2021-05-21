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

from ddd.logic.learning_unit.builder.effective_class_builder import EffectiveClassBuilder
from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from infrastructure.learning_unit.repository.effective_class import EffectiveClassRepository
from infrastructure.learning_unit.repository.learning_unit import LearningUnitRepository
from osis_common.ddd import interface


class CreateClassService(interface.DomainService):

    @classmethod
    def create(
            cls,
            cmd: 'CreateEffectiveClassCommand'
    ) -> 'EffectiveClassIdentity':
        # Given
        repository = LearningUnitRepository()
        learning_unit = repository.get(
            entity_id=LearningUnitIdentityBuilder.build_from_code_and_year(cmd.learning_unit_code, cmd.year)
        )
        class_repository = EffectiveClassRepository()
        all_existing_class_identities = class_repository.get_identities()
        # When
        effective_class = EffectiveClassBuilder.build_from_command(
            cmd,
            learning_unit,
            all_existing_class_identities
        )
        # Then
        return effective_class
