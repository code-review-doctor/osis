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
import itertools
from typing import List

from ddd.logic.attribution.domain.service.i_tutor_attribution import ITutorAttributionToLearningUnitTranslator
from ddd.logic.attribution.dtos import TutorAttributionToLearningUnitDTO, TutorDTO
from ddd.logic.attribution.repository.i_tutor import ITutorRepository
from ddd.logic.learning_unit.domain.model.effective_class import EffectiveClassIdentity
from osis_common.ddd import interface


class ClassDistributionWithAttribution(interface.DomainService):

    @classmethod
    def search_by_effective_class(
            cls,
            effective_class_identity: 'EffectiveClassIdentity',
            tutor_attribution_translator: 'ITutorAttributionToLearningUnitTranslator',
            tutor_repository: 'ITutorRepository'
    ) -> List['TutorDTO']:
        attributions = tutor_attribution_translator.search_attributions_to_learning_unit(
            effective_class_identity.learning_unit_identity
        )

        result = []
        for tutor in tutor_repository.search(effective_class_identity=effective_class_identity):
            for effective_class in tutor.distributed_effective_classes:
                attribution = next(
                    att for att in attributions if att.attribution_uuid == effective_class.attribution.uuid
                )
                result.append(
                    TutorDTO(
                        attribution_uuid=effective_class.attribution.id,
                        last_name=attribution.last_name,
                        first_name=attribution.first_name.id,
                        function=attribution.function,
                        distributed_volume_to_class=effective_class.distributed_volume,
                    )
                )

        return result
