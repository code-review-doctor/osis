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
from typing import List, Optional, Set

from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity, EffectiveClass
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from ddd.logic.learning_unit.dtos import EffectiveClassFromRepositoryDTO
from osis_common.ddd import interface
from osis_common.ddd.interface import ApplicationService


class IEffectiveClassRepository(interface.AbstractRepository):

    @classmethod
    @abc.abstractmethod
    def search(cls, entity_ids: Optional[List[EffectiveClassIdentity]] = None, **kwargs) -> List[EffectiveClass]:
        pass

    @classmethod
    @abc.abstractmethod
    def search_dtos_by_learning_unit(
            cls,
            learning_unit_id: Optional[LearningUnitIdentity] = None,
            **kwargs
    ) -> List['EffectiveClassFromRepositoryDTO']:
        pass

    @classmethod
    @abc.abstractmethod
    def delete(cls, entity_id: EffectiveClassIdentity, **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def save(cls, entity: EffectiveClass) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def get_all_identities(cls) -> List['EffectiveClassIdentity']:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get(cls, entity_id: 'EffectiveClassIdentity') -> 'EffectiveClass':
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def search_dtos(cls, codes: Set[str], annee: int) -> List['EffectiveClassFromRepositoryDTO']:
        pass

    @classmethod
    @abc.abstractmethod
    def get_dto(cls, code: str, annee: int) -> 'EffectiveClassFromRepositoryDTO':
        pass
