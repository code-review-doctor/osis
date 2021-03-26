import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class CreateLearningUnitCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    academic_year = attr.ib(type=int)
    type = attr.ib(type=str)
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

    @code.validator
    def _code(self):

    def should_be_valid(self):
        errors = []
        if not isinstance(self.code, str):
            errors += InvalidValueException("MessageText")
        if not self.code:
            errors += FieldRequiredException('Message Text')
        if errors:
            raise MultipleBusinessException(exceptions=errors)


@attr.s(frozen=True, slots=True)
class CreatePartimCommand(interface.CommandRequest):
    learning_unit_code = attr.ib(type=str)
    learning_unit_year = attr.ib(type=int)
    subdivision = attr.ib(type=int)
    title_fr = attr.ib(type=str)
    title_en = attr.ib(type=str)
    credits = attr.ib(type=int)
    periodicity = attr.ib(type=str)
    iso_code = attr.ib(type=str)
    remark_faculty = attr.ib(type=str)
    remark_publication_fr = attr.ib(type=str)
    remark_publication_en = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DeleteLearningUnitCommand(interface.CommandRequest):
    code = attr.ib(type=str)
    academic_year = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class CopyLearningUnitToNextYearCommand(interface.CommandRequest):
    copy_from_code = attr.ib(type=str)
    copy_from_year = attr.ib(type=int)
