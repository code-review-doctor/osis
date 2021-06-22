import abc

from ddd.logic.attribution.domain.model.tutor import TutorIdentity
from ddd.logic.attribution.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from osis_common.ddd import interface


class ITutorAttributionToLearningUnitTranslator(interface.DomainService):

    @classmethod
    @abc.abstractmethod
    def get_tutor_attribution_to_learning_unit(
            cls,
            tutor_identity: 'TutorIdentity',
            learning_unit_identity: 'LearningUnitIdentity'
    ) -> 'TutorAttributionToLearningUnitDTO':
        pass
