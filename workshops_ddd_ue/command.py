import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class CreateLearningUnitCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    academic_year = attr.ib(type=int)
    common_title_fr = attr.ib(type=str)
    specific_title_fr = attr.ib(type=str)
    common_title_en = attr.ib(type=str)
    specific_title_en = attr.ib(type=str)
    credits = attr.ib(type=int)
    internship_subtype = attr.ib(type=str)
    responsible_entity_code = attr.ib(type=str)
    periodicity = attr.ib(type=str)
    iso_code = attr.ib(type=str)
    remark_faculty = attr.ib(type=str)
    remark_publication_fr = attr.ib(type=str)
    remark_publication_en = attr.ib(type=str)
