import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class ApplicationCalendarIdentity(interface.EntityIdentity):
    uuid = attr.ib(type=str)


@attr.s(slots=True, hash=False, eq=False)
class ApplicationCalendar(interface.RootEntity):
    entity_id = attr.ib(type=ApplicationCalendarIdentity)
    authorized_target_year = attr.ib(type=str)
    start_date = attr.ib(type=str)
    end_date = attr.ib(type=str)
