import attr

from base.models.enums.entity_type import EntityType
from osis_common.ddd import interface
from workshops_ddd_ue.domain._address import Address


@attr.s(frozen=True, slots=True)
class ResponsibleEntityIdentity(interface.EntityIdentity):
    code = attr.ib(type=str)


@attr.s(slots=True, hash=False, eq=False)
class ResponsibleEntity(interface.Entity):
    entity_id = attr.ib(type=ResponsibleEntityIdentity)
    title = attr.ib(type=str)
    address = attr.ib(type=Address)
    type = attr.ib(type=EntityType)

    @property
    def code(self) -> str:
        return self.entity_id.code