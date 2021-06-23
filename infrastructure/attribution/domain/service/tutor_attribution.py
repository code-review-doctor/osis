from typing import List

from django.db.models import F

from attribution.models.attribution_charge_new import AttributionChargeNew
from ddd.logic.attribution.domain.model.tutor import TutorIdentity
from ddd.logic.attribution.domain.service.i_tutor_attribution import ITutorAttributionToLearningUnitTranslator
from ddd.logic.attribution.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity


class TutorAttributionToLearningUnitTranslator(ITutorAttributionToLearningUnitTranslator):

    @classmethod
    def search_attributions_to_learning_unit(
            cls,
            learning_unit_identity: 'LearningUnitIdentity'
    ) -> List['TutorAttributionToLearningUnitDTO']:
        qs = AttributionChargeNew.objects.filter(
            learning_component_year__learning_unit_year__acronym=learning_unit_identity.code,
            learning_component_year__learning_unit_year__academic_year__year=learning_unit_identity.year,
        ).annotate(
            attribution_uuid=F('attribution__uuid'),
            first_name=F('attribution__tutor__person__first_name'),
            last_name=F('attribution__tutor__person__first_name'),
            personal_id_number=F('attribution__tutor__person__global_id'),
            function=F('attribution__function'),
            attributed_volume_to_learning_unit=F('allocation_charge'),
        ).values(
            'attribution_uuid',
            'first_name',
            'last_name',
            'personal_id_number',
            'function',
            'attributed_volume_to_learning_unit',
        )
        return [TutorAttributionToLearningUnitDTO(**data_as_dict) for data_as_dict in qs]

    @classmethod
    def get_tutor_attribution_to_learning_unit(
            cls,
            tutor_identity: 'TutorIdentity',
            learning_unit_identity: 'LearningUnitIdentity'
    ) -> 'TutorAttributionToLearningUnitDTO':
        attributions_to_learn_unit = cls.search_attributions_to_learning_unit(learning_unit_identity)
        return next(
            (
                att for att in attributions_to_learn_unit
                if att.personal_id_number == tutor_identity.personal_id_number
            ),
            None
        )
