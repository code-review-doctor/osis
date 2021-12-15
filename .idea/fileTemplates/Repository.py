#set( $aggregate = ${StringUtils.removeAndHump($NAME)} )
from typing import Optional, List

class ${aggregate}Repository(I${aggregate}):
    @classmethod
    def get(cls, entity_id: '${aggregate}Identity') -> '${aggregate}':
        raise NotImplementedError

    @classmethod
    def search(cls, entity_ids: Optional[List['${aggregate}Identity']] = None, **kwargs) -> List['${aggregate}']:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: '${aggregate}Identity', **kwargs) -> None:
        raise NotImplementedError

    @classmethod
    def save(cls, entity: '${aggregate}') -> None:
        raise NotImplementedError
