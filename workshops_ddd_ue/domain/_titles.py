import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class Titles(interface.ValueObject):
    common_fr = attr.ib(type=str)
    specific_fr = attr.ib(type=str)
    common_en = attr.ib(type=str)
    specific_en = attr.ib(type=str)
