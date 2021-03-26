from base.ddd.utils.business_validator import BusinessValidator
from base.models.enums.entity_type import EntityType
from workshops_ddd_ue.domain.exceptions import InvalidResponsibleEntityTypeOrCodeException
from workshops_ddd_ue.domain.responsible_entity import ResponsibleEntity


class ResponsibleEntityAuthorizedTypeOrCode(BusinessValidator):

    def __init__(self, responsible_entity_code: str, responsible_entity_type: str):
        super().__init__()
        self.responsible_entity_code = responsible_entity_code
        self.responsible_entity_type = responsible_entity_type

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
        if not(self.responsible_entity_type in authorized_types or self.responsible_entity_code in authorized_codes):
            raise InvalidResponsibleEntityTypeOrCodeException(
                authorized_types=authorized_types,
                authorized_codes=authorized_codes
            )
