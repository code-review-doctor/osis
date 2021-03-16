import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class AcademicYear(interface.ValueObject):
    year = attr.ib(type=int)

    def __str__(self):
        # 2021-22
        return "{}-{}".format(self.year, self.year + 1)
