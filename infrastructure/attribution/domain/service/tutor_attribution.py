##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
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
            learning_unit_code=F('learning_component_year__learning_unit_year__acronym'),
            learning_unit_year=F('learning_component_year__learning_unit_year__academic_year__year'),
            attribution_uuid=F('attribution__uuid'),
            first_name=F('attribution__tutor__person__first_name'),
            last_name=F('attribution__tutor__person__last_name'),
            personal_id_number=F('attribution__tutor__person__global_id'),
            function=F('attribution__function'),
            attributed_volume_to_learning_unit=F('allocation_charge'),
            component_type=F('learning_component_year__type'),
        ).values(
            'learning_unit_code',
            'learning_unit_year',
            'attribution_uuid',
            'first_name',
            'last_name',
            'personal_id_number',
            'function',
            'attributed_volume_to_learning_unit',
            'component_type'
        ).order_by(
            'last_name',
            'first_name',
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

    @classmethod
    def get_learning_unit_attribution(
            cls,
            attribution_uuid: str,
            learning_unit_identity: 'LearningUnitIdentity'
    ) -> 'TutorAttributionToLearningUnitDTO':
        # TODO : ??? pq ne pas ajouter le uuid dans le search
        attributions_to_learn_unit = cls.search_attributions_to_learning_unit(learning_unit_identity)
        return next(
            (
                att for att in attributions_to_learn_unit
                if str(att.attribution_uuid) == attribution_uuid
            ),
            None
        )
