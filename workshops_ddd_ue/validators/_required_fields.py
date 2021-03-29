import attr

from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.command import CreateLearningUnitCommand
from workshops_ddd_ue.domain.exceptions import EmptyRequiredFieldsException


@attr.s(frozen=True, slots=True)
class RequiredFieldsValidator(BusinessValidator):

    command = attr.ib(type=CreateLearningUnitCommand)

    def validate(self, *args, **kwargs):
        mandatory_field = [
            'code',
            'academic_year',
            'common_title_fr',
            'specific_title_fr',
            'credits',
            'internship_subtype',
            'responsible_entity_code',
            'periodicity',
            'iso_code',
        ]
        empty_required_fields = []
        for field in mandatory_field:
            if not getattr(self.command, field, False):
                empty_required_fields.append(field)
        if empty_required_fields:
            raise EmptyRequiredFieldsException(empty_required_fields=empty_required_fields)
