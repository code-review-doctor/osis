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
import datetime
from typing import List

from attribution.models.enums.function import Functions
from ddd.logic.effective_class_repartition.domain.service.i_tutor_attribution import \
    ITutorAttributionToLearningUnitTranslator
from ddd.logic.effective_class_repartition.dtos import TutorAttributionToLearningUnitDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity


class TutorAttributionToLearningUnitTranslatorInMemory(ITutorAttributionToLearningUnitTranslator):

    attributions = [
        TutorAttributionToLearningUnitDTO(
            learning_unit_code='LDROI1001',
            learning_unit_year=datetime.date.today().year,
            attribution_uuid='attribution_uuid1',
            last_name='Smith',
            first_name='Charles',
            personal_id_number='00321234',
            function=Functions.COORDINATOR.name,
            lecturing_volume_attributed=10.0,
            practical_volume_attributed=15.0,
        ),
        TutorAttributionToLearningUnitDTO(
            learning_unit_code='LDROI1001',
            learning_unit_year=datetime.date.today().year,
            attribution_uuid='attribution_uuid2',
            last_name='Smith',
            first_name='Bastos',
            personal_id_number='00321235',
            function=Functions.CO_HOLDER.name,
            lecturing_volume_attributed=1.0,
            practical_volume_attributed=5.0,
        ),
    ]

    @classmethod
    def search_attributions_to_learning_unit(
            cls,
            learning_unit_identity: 'LearningUnitIdentity',
    ) -> List['TutorAttributionToLearningUnitDTO']:
        return list(
            filter(
                lambda dto: _filter(dto, learning_unit_identity),
                cls.attributions
            )
        )

    @classmethod
    def get_learning_unit_attribution(cls, attribution_uuid: str) -> 'TutorAttributionToLearningUnitDTO':
        return next(att for att in cls.attributions if att.attribution_uuid == attribution_uuid)

    @classmethod
    def get_by_enseignant(cls, matricule_fgs_enseignant: str, annee: int) -> List['TutorAttributionToLearningUnitDTO']:
        return [
            att for att in cls.attributions
            if att.personal_id_number == matricule_fgs_enseignant and att.learning_unit_year == annee
        ]


def _filter(dto, learning_unit_identity):
    return dto.learning_unit_code == learning_unit_identity.code \
           and dto.learning_unit_year == learning_unit_identity.academic_year.year
