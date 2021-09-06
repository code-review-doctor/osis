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
from ddd.logic.learning_unit.builder.effective_class_identity_builder import EffectiveClassIdentityBuilder
from ddd.logic.learning_unit.commands import GetEffectiveClassCommand
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass
from ddd.logic.learning_unit.repository.i_effective_class import IEffectiveClassRepository


# FIXME :: à tester unitairement + renvoyer EffectiveClassFromRepositoryDTO au lieu de l'objet du domaine
def get_effective_class(
        cmd: 'GetEffectiveClassCommand',
        effective_class_repository: 'IEffectiveClassRepository'
) -> 'EffectiveClass':

    effective_class_identity = EffectiveClassIdentityBuilder.build_from_code_and_learning_unit_identity_data(
        class_code=cmd.class_code,
        learning_unit_code=cmd.learning_unit_code,
        learning_unit_year=cmd.learning_unit_year
    )
    return effective_class_repository.get(entity_id=effective_class_identity)
