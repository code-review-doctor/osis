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
import abc
from typing import List, Set, Tuple

from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity, LearningUnit
from ddd.logic.learning_unit.dtos import LearningUnitSearchDTO
from osis_common.ddd import interface


class ILearningUnitRepository(interface.AbstractRepository):
    @classmethod
    @abc.abstractmethod
    def get(cls, entity_id: 'LearningUnitIdentity') -> 'LearningUnit':
        pass

    @classmethod
    @abc.abstractmethod
    def search_learning_units_dto(
            cls,
            code_annee_values: Set[Tuple[str, int]] = None,
            code: str = None,
            annee_academique: int = None,
            intitule: str = None
    ) -> List['LearningUnitSearchDTO']:
        pass

    @classmethod
    @abc.abstractmethod
    def has_proposal_this_year_or_in_past(cls, learning_unit: 'LearningUnit') -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def has_enrollments(cls, learning_unit: 'LearningUnit') -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def get_all_identities(cls) -> List['LearningUnitIdentity']:
        pass
