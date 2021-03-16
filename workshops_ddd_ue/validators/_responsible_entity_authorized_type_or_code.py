from base.ddd.utils.business_validator import BusinessValidator
from base.models.enums.entity_type import EntityType
from workshops_ddd_ue.domain.exceptions import InvalidResponsibleEntityTypeOrCodeException
from workshops_ddd_ue.domain.learning_unit_year import ResponsibleEntity


class ResponsibleEntityAuthorizedTypeOrCode(BusinessValidator):

    def __init__(self, responsible_entity: 'ResponsibleEntity'):
        super().__init__()
        self.responsible_entity = responsible_entity

    def validate(self, *args, **kwargs):
        authorized_types = [
            EntityType.SECTOR,
            EntityType.FACULTY,
            EntityType.SCHOOL,
            EntityType.DOCTORAL_COMMISSION,
        ]
        authorized_codes = [
            "ILV",
            "IUFC",
            "CCR",
            "LLL",
        ]
        if not(self.responsible_entity.type in authorized_types or self.responsible_entity.code in authorized_codes):
            raise InvalidResponsibleEntityTypeOrCodeException(
                authorized_types=authorized_types,
                authorized_codes=authorized_codes
            )
