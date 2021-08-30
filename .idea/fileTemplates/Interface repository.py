#set( $Aggregate = ${StringUtils.removeAndHump($NAME)} )
import abc
from typing import List, Optional

from osis_common.ddd import interface


class I${Aggregate}Repository(interface.AbstractRepository):
    @classmethod
    @abc.abstractmethod
    def get(cls, entity_id: '${Aggregate}Identity') -> '${Aggregate}':
        pass

    @classmethod
    @abc.abstractmethod
    def search(
            cls,
            entity_ids: Optional[List['${Aggregate}Identity']] = None,
            matricule_candidat: str = None,
            **kwargs
    ) -> List['${Aggregate}']:
        pass

    @classmethod
    @abc.abstractmethod
    def delete(cls, entity_id: '${Aggregate}Identity', **kwargs) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def save(cls, entity: '${Aggregate}') -> None:
        pass