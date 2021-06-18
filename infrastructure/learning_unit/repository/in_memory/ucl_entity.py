from typing import Optional, List

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository
from ddd.logic.learning_unit.domain.model.responsible_entity import UclEntity
from ddd.logic.learning_unit.repository.i_ucl_entity import IUclEntityRepository
from osis_common.ddd.interface import EntityIdentity


class UclEntityRepository(InMemoryGenericRepository, IUclEntityRepository):
    entities = list()  # type: List[UclEntity]

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List['UclEntity']:
        raise NotImplementedError
