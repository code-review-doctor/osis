from typing import Optional, List

from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity, LearningUnit
from ddd.logic.learning_unit.dtos import LearningUnitSearchDTO
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository
from osis_common.ddd.interface import ApplicationService


class LearningUnitRepository(ILearningUnitRepository):
    learning_units = list()  # type: List['LearningUnit']

    @classmethod
    def search_learning_units_dto(
            cls,
            code: str = None,
            year: int = None,
            full_title: str = None,
            type: str = None,
            responsible_entity_code: str = None
    ) -> List['LearningUnitSearchDTO']:
        pass

    # TODO: To implement when Proposals are in DDD
    @classmethod
    def has_proposal(cls, learning_unit: 'LearningUnit') -> bool:
        return False

    # TODO: To implement when Enrollments are in DDD
    @classmethod
    def has_enrollments(cls, learning_unit: 'LearningUnit') -> bool:
        return False

    @classmethod
    def get(cls, entity_id: 'LearningUnitIdentity') -> 'LearningUnit':
        for lu in cls.learning_units:
            if lu.entity_id == entity_id:
                return lu
        return None

    @classmethod
    def search(cls, entity_ids: Optional[List['LearningUnitIdentity']] = None, **kwargs) -> List['LearningUnit']:
        pass

    @classmethod
    def delete(cls, entity_id: 'LearningUnitIdentity', **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def save(cls, entity: 'LearningUnit') -> None:
        cls.learning_units.append(entity)

    @classmethod
    def get_all_identities(cls) -> List['LearningUnitIdentity']:
        return [lu.entity_id for lu in cls.learning_units]
