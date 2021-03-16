import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class Remarks(interface.ValueObject):
    faculty = attr.ib(type=str)
    publication_fr = attr.ib(type=str)
    publication_en = attr.ib(type=str)
