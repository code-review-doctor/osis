from ddd.logic.attribution.domain.model.tutor import TutorIdentity
from ddd.logic.attribution.domain.service.i_tutor_attribution import ITutorAttributionToLearningUnitTranslator
from ddd.logic.attribution.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity


class TutorAttributionToLearningUnitTranslator(ITutorAttributionToLearningUnitTranslator):

    @classmethod
    def get_tutor_attribution_to_learning_unit(
            cls,
            tutor_identity: 'TutorIdentity',
            learning_unit_identity: 'LearningUnitIdentity'
    ) -> 'TutorAttributionToLearningUnitDTO':
        # AttributionChergeNew.objects...
        # return TutorAttributionToLearningUnitDTO(qs.values())
        raise NotImplementedError  # Call Django queryset
