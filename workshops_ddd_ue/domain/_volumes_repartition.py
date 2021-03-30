from decimal import Decimal

import attr

from base.models.enums.quadrimesters import DerogationQuadrimester
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class Duration(interface.ValueObject):
    hours = attr.ib(type=int)
    minutes = attr.ib(type=int)

    @property
    def quantity_in_hours(self) -> Decimal:
        return Decimal(self.hours + self.minutes)  # FIXME


@attr.s(frozen=True, slots=True)
class Volumes(interface.ValueObject):
    volume_first_quadrimester = attr.ib(type=Duration)
    volume_second_quadrimester = attr.ib(type=Duration)
    volume_annual = attr.ib(type=Duration)
    derogation_quadrimester = attr.ib(type=DerogationQuadrimester)


@attr.s(frozen=True, slots=True)
class LecturingPart(interface.ValueObject):
    acronym = 'PM'
    volumes = attr.ib(type=Volumes)


@attr.s(frozen=True, slots=True)
class PracticalPart(interface.ValueObject):
    acronym = 'PP'
    volumes = attr.ib(type=Volumes)
