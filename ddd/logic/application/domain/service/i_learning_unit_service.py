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

from ddd.logic.application.dtos import LearningUnitVolumeFromServiceDTO, LearningUnitTutorAttributionFromServiceDTO, \
    LearningUnitAnnualVolumeFromServiceDTO
from ddd.logic.learning_unit.domain.model.learning_unit import LearningUnitIdentity
from osis_common.ddd import interface


class ILearningUnitService(interface.DomainService):
    """
        Anticorruption layer to translate data from learning_unit bounded context to application bounded context
    """
    def search_learning_unit_volumes_dto(
            self,
            entity_ids: List[LearningUnitIdentity]
    ) -> List[LearningUnitVolumeFromServiceDTO]:
        pass

    def search_tutor_attribution_dto(
            self,
            entity_ids: List[LearningUnitIdentity]
    ) -> List[LearningUnitTutorAttributionFromServiceDTO]:
        pass

    def search_learning_unit_annual_volume_dto(
            self,
            entity_id: LearningUnitIdentity
    ) -> LearningUnitAnnualVolumeFromServiceDTO:
        pass
