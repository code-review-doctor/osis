import functools
import operator
from typing import List

from django.db.models import Q, F

from base.models.learning_unit_year import LearningUnitYear
from ddd.logic.application.domain.service.i_learning_unit_service import ILearningUnitService
from ddd.logic.application.dtos import LearningUnitVolumeDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity


class LearningUnitTranslator(ILearningUnitService):
    # TODO: Refactor use learning unit service instead
    def search_learning_unit_volumes_dto(self, entity_ids: List[LearningUnitIdentity]) -> List[LearningUnitVolumeDTO]:
        filter_clause = functools.reduce(
            operator.or_,
            (
                (Q(acronym=entity_id.code) & Q(academic_year__year=entity_id.academic_year.year))
                for entity_id in entity_ids
            )
        )

        qs = LearningUnitYear.objects.filter(filter_clause).\
            annotate_volume_total().\
            annotate(
                code=F('acronym'),
                year=F('academic_year__year')
            ).\
            values(
                'code',
                'year',
                'lecturing_volume_total',
                'practical_volume_total',
            )
        return [LearningUnitVolumeDTO(**row_as_dict) for row_as_dict in qs]
