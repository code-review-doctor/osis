import attr

from base.models.enums.entity_type import EntityType
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class ResponsibleEntityIdentity(interface.EntityIdentity):
    code = attr.ib(type=str)


@attr.s(slots=True, hash=False, eq=False)
class ResponsibleEntity(interface.RootEntity):
    entity_id = attr.ib(type=ResponsibleEntityIdentity)
    type = attr.ib(type=EntityType)

    @property
    def code(self) -> str:
        return self.entity_id.code

    def is_sector(self):
        return self.type == EntityType.SECTOR

    def is_faculty(self):
        return self.type == EntityType.FACULTY

    def is_school(self):
        return self.type == EntityType.SCHOOL

    def is_doctoral_commission(self):
        return self.type == EntityType.DOCTORAL_COMMISSION

