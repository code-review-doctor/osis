import attr

from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import SubdivisionAlreadyExistException
from workshops_ddd_ue.domain.learning_unit_year import LearningUnit


@attr.s(frozen=True, slots=True)
class SubdivisionShouldNotExistValidator(BusinessValidator):

    subdivision = attr.ib(tpye=str)
    learning_unit = attr.ib(tpye=LearningUnit)

    def validate(self, *args, **kwargs):
        if self.learning_unit.contains_partim_subdivision(self.subdivision):
            raise SubdivisionAlreadyExistException(self.learning_unit.entity_id, self.subdivision)
