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
from typing import Optional, List

from ddd.logic.learning_unit.builder.learning_unit_identity_builder import LearningUnitIdentityBuilder
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClass, EffectiveClassIdentity
from ddd.logic.learning_unit.repository.i_effective_class import IEffectiveClassRepository
from osis_common.ddd.interface import EntityIdentity, ApplicationService
from learning_unit.models.learning_class_year import LearningClassYear as LearningClassYearDatabase


class EffectiveClassRepository(IEffectiveClassRepository):
    @classmethod
    def get(cls, entity_id: EntityIdentity) -> 'EffectiveClass':
        raise NotImplementedError

    @classmethod
    def search(cls, entity_ids: Optional[List['EffectiveClassIdentity']] = None, **kwargs) -> List['EffectiveClass']:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: 'EffectiveClassIdentity', **kwargs: ApplicationService) -> None:
        raise NotImplementedError

    @classmethod
    def save(cls, entity: 'EffectiveClass') -> None:
        raise NotImplementedError

    @classmethod
    def get_all_identities(cls) -> List['EffectiveClassIdentity']:
        all_learn_unit_years = LearningClassYearDatabase.objects.all().values(
            "acronym"
            "learning_component_year__learning_unit_year__acronym",
            "learning_component_year__learning_unit_year__academic_year__year",
        )

        return [
            EffectiveClassIdentity(
                class_code=learning_unit['acronym'],
                learning_unit_identity=LearningUnitIdentityBuilder.build_from_code_and_year(
                    learning_unit['learning_component_year__learning_unit_year__acronym'],
                    learning_unit['learning_component_year__learning_unit_year__academic_year__year']
                )
            )
            for learning_unit in all_learn_unit_years
        ]
