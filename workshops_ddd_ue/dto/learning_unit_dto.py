import attr


# TODO :: to move into osis_common.ddd.interface
class DTO:
    """
    Data Transfer Object : only contains declaration of primitive fields.
    Used as 'contract" between 2 layers in the code (example : repository <-> factory)
    """
    pass


@attr.s(frozen=True, slots=True)
class LearningUnitFromRepositoryDTO(DTO):
    code = attr.ib(type=str)
    year = attr.ib(type=int)
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
