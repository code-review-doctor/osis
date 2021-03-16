import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class Language(interface.ValueObject):
    ietf_code = attr.ib(type=str)  # FR_BE, EN...
    name = attr.ib(type=str)
    iso_code = attr.ib(type=str)
