import attr

from ddd.logic.shared_kernel.academic_year.domain.model.academic_year import AcademicYearIdentity
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class ApplicationCalendarIdentity(interface.EntityIdentity):
    uuid = attr.ib(type=str)


@attr.s(slots=True, hash=False, eq=False)
class ApplicationCalendar(interface.RootEntity):
    entity_id = attr.ib(type=ApplicationCalendarIdentity)
    authorized_target_year = attr.ib(type=AcademicYearIdentity)
    start_date = attr.ib(type=str)
    end_date = attr.ib(type=str)
