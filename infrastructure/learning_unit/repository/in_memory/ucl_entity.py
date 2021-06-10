from typing import Optional, List

from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity, LearningUnit
from ddd.logic.learning_unit.domain.model.responsible_entity import UclEntity, UCLEntityIdentity
from ddd.logic.learning_unit.dtos import LearningUnitSearchDTO
from ddd.logic.learning_unit.repository.i_learning_unit import ILearningUnitRepository
from ddd.logic.learning_unit.repository.i_ucl_entity import IUclEntityRepository
from osis_common.ddd.interface import ApplicationService, EntityIdentity


class UclEntityRepository(IUclEntityRepository):
    ucl_entities = list()  # type: List[UclEntity]

    @classmethod
    def get(cls, entity_id: 'UCLEntityIdentity') -> 'UclEntity':
        return next(
            (entity for entity in cls.ucl_entities if entity.entity_id == entity_id),
            None
        )

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List['UclEntity']:
        pass

    @classmethod
    def delete(cls, entity_id: 'UCLEntityIdentity', **kwargs: ApplicationService) -> None:
        pass

    @classmethod
    def save(cls, entity: 'UclEntity') -> None:
        cls.ucl_entities.append(entity)
