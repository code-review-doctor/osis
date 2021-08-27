#set( $aggregate = ${StringUtils.removeAndHump($NAME)} )
from typing import Optional, List

from base.ddd.utils.in_memory_repository import InMemoryGenericRepository


class ${aggregate}InMemoryRepository(InMemoryGenericRepository, I${aggregate}Repository):
    entities = list()  # type: List[${aggregate}]

    @classmethod
    def search(cls, entity_ids: Optional[List['${aggregate}Identity']] = None, **kwargs) -> List['${aggregate}']:
        return [e for e in self.entites if e.entity_id in entity_ids]

    @classmethod
    def reset(cls):
        cls.entities = []
