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
from ddd.logic.effective_class_repartition.domain.model.tutor import TutorIdentity
from ddd.logic.effective_class_repartition.domain.service.i_tutor_attribution import ITutorAttributionToLearningUnitTranslator
from ddd.logic.effective_class_repartition.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity


class TutorAttributionToLearningUnitTranslator(ITutorAttributionToLearningUnitTranslator):
    dtos = []  # type: List[TutorAttributionToLearningUnitDTO]

    @classmethod
    def get_tutor_attribution_to_learning_unit(
            cls,
            tutor_identity: 'TutorIdentity',
            learning_unit_identity: 'LearningUnitIdentity'
    ) -> 'TutorAttributionToLearningUnitDTO':
        dtos = cls.search_attributions_to_learning_unit(learning_unit_identity)
        return next(
            (
                dto for dto in dtos
                if dto.personal_id_number == tutor_identity.personal_id_number
            ),
            None
        )

    @classmethod
    def search_attributions_to_learning_unit(
            cls,
            learning_unit_identity: 'LearningUnitIdentity'
    ) -> List['TutorAttributionToLearningUnitDTO']:
        return list(
            (
                dto for dto in cls.dtos
                if dto.learning_unit_code == learning_unit_identity.code
                and dto.learning_unit_year == learning_unit_identity.year
            )
        )
