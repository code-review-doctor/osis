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
from ddd.logic.attribution.builder.learning_unit_attribution_identity_builder import \
    LearningUnitAttributionIdentityBuilder
from ddd.logic.attribution.domain.model._attribution import LearningUnitAttribution

from osis_common.ddd import interface


class LearningUnitAttributionBuilder(interface.RootEntityBuilder):

    @classmethod
    def build_from_repository_dto(
            cls,
            learning_unit_identity: 'LearningUnitIdentity',
            dto_object: 'LearningUnitAttributionDTO') \
            -> 'LearningUnitAttribution':
        entity_id = LearningUnitAttributionIdentityBuilder.build_from_code_and_learning_unit_identity_data(
            uuid=dto_object.attribution_uuid
        )
        return LearningUnitAttribution(
            entity_id=entity_id,
            function=dto_object.function,
            learning_unit=learning_unit_identity,
            distributed_effective_classes=[]  # TODO tocomplete
        )
