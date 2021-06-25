from typing import Optional, List

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity, LearningUnit
from ddd.logic.learning_unit.dtos import LearningUnitSearchDTO
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository


class LearningUnitRepository(InMemoryGenericRepository, ILearningUnitRepository):
    entities = list()  # type: List[LearningUnit]

    @classmethod
    def search(cls, entity_ids: Optional[List['LearningUnitIdentity']] = None, **kwargs) -> List['LearningUnit']:
        raise NotImplementedError

    @classmethod
    def search_learning_units_dto(
            cls,
            code: str = None,
            year: int = None,
            full_title: str = None,
            type: str = None,
            responsible_entity_code: str = None
    ) -> List['LearningUnitSearchDTO']:
        raise NotImplementedError

    # TODO: To implement when Proposals are in DDD
    @classmethod
    def has_proposal_this_year_or_in_past(cls, learning_unit: 'LearningUnit') -> bool:
        return False

    # TODO: To implement when Enrollments are in DDD
    @classmethod
    def has_enrollments(cls, learning_unit: 'LearningUnit') -> bool:
        return False
