from typing import Optional, List

from osis_common.ddd import interface
from osis_common.ddd.interface import EntityIdentity, ApplicationService, Entity
from workshops_ddd_ue.domain.responsible_entity import ResponsibleEntity


class EntityRepository(interface.AbstractRepository):
    @classmethod
    def create(cls, entity: Entity, **kwargs: ApplicationService) -> EntityIdentity:
        pass

    @classmethod
    def update(cls, entity: Entity, **kwargs: ApplicationService) -> EntityIdentity:
        pass

    @classmethod
    def get(cls, entity_id: EntityIdentity) -> 'ResponsibleEntity':
        pass

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List[Entity]:
        pass

    @classmethod
    def delete(cls, entity_id: EntityIdentity, **kwargs: ApplicationService) -> None:
        pass
