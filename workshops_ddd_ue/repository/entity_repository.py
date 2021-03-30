from typing import Optional, List

from base.models.entity_version import EntityVersion
from osis_common.ddd import interface
from osis_common.ddd.interface import EntityIdentity, ApplicationService, Entity, RootEntity
from workshops_ddd_ue.builder.responsible_entity_identity_builder import ResponsibleEntityIdentityBuilder
from workshops_ddd_ue.domain.responsible_entity import ResponsibleEntity, ResponsibleEntityIdentity


class EntityRepository(interface.AbstractRepository):
    @classmethod
    def save(cls, entity: RootEntity) -> None:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'ResponsibleEntityIdentity') -> 'ResponsibleEntity':
        entity_version = EntityVersion.objects.get(acronym=entity_id.code)
        return ResponsibleEntity(
            entity_id=ResponsibleEntityIdentityBuilder.build_from_code(code=entity_version.acronym),
            type=entity_version.entity_type
        )  # FIXME :: reuse Builder instead

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List[Entity]:
        pass

    @classmethod
    def delete(cls, entity_id: EntityIdentity, **kwargs: ApplicationService) -> None:
        pass
