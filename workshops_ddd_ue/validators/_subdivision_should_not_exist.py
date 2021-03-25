from base.ddd.utils.business_validator import BusinessValidator
from workshops_ddd_ue.domain.exceptions import SubdivisionAlreadyExistException
from workshops_ddd_ue.domain.learning_unit_year import LearningUnit


class SubdivisionShouldNotExistValidator(BusinessValidator):

    def __init__(self, subdivision: str, learning_unit: 'LearningUnit'):
        super().__init__()
        self.subdivision = subdivision
        self.learning_unit = learning_unit

    def validate(self, *args, **kwargs):
        if self.learning_unit.contains_partim_subdivision(self.subdivision):
            raise SubdivisionAlreadyExistException(self.learning_unit.entity_id, self.subdivision)
