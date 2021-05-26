from typing import Optional, List

from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity, LearningUnit
from ddd.logic.learning_unit.repository.i_effective_class import IEffectiveClassRepository
from osis_common.ddd.interface import ApplicationService


class LearningUnitRepository(IEffectiveClassRepository):
    learning_units = list()

    @classmethod
    def get(cls, entity_id: LearningUnitIdentity) -> LearningUnit:
        for lu in cls.learning_units:
            if lu.entity_id == entity_id:
                return lu
        return None

    @classmethod
    def search(cls, entity_ids: Optional[List[LearningUnitIdentity]] = None, **kwargs) -> List[LearningUnit]:
        pass

    @classmethod
    def delete(cls, entity_id: LearningUnitIdentity, **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def save(cls, entity: LearningUnit) -> None:
        cls.learning_units.append(entity)

    @classmethod
    def get_all_identities(cls) -> List['LearningUnitIdentity']:
        return [lu.entity_id for lu in cls.learning_units]
