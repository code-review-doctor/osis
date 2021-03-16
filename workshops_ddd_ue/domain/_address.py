import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class Address(interface.ValueObject):
    country = attr.ib(type=str)
    street_name = attr.ib(type=str)
    street_number = attr.ib(type=str)
    city = attr.ib(type=str)
    postal_code = attr.ib(type=str)