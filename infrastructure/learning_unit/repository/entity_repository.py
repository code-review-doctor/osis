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
from typing import Optional, List

from django.db.models import F

from base.models.entity_version import EntityVersion
from base.models.enums.entity_type import EntityType
from ddd.logic.learning_unit.builder.responsible_entity_builder import ResponsibleEntityBuilder
from ddd.logic.learning_unit.builder.responsible_entity_identity_builder import ResponsibleEntityIdentityBuilder
from ddd.logic.learning_unit.domain.model.responsible_entity import ResponsibleEntityIdentity, ResponsibleEntity
from ddd.logic.learning_unit.dtos import ResponsibleEntityDataDTO
from ddd.logic.learning_unit.repository.i_responsible_entity import IResponsibleEntityRepository
from osis_common.ddd.interface import EntityIdentity, ApplicationService, Entity, RootEntity


class ResponsibleEntityRepository(IResponsibleEntityRepository):
    @classmethod
    def save(cls, entity: RootEntity) -> None:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'ResponsibleEntityIdentity') -> 'ResponsibleEntity':
        entity_version_as_dict = EntityVersion.objects.filter(
            acronym=entity_id.code
        ).annotate(
            code=F('acronym'),
            type=F('entity_type'),
        ).values(
            'code',
            'type',
        ).get()
        dto = ResponsibleEntityDataDTO(**entity_version_as_dict)
        return ResponsibleEntityBuilder.build_from_repository_dto(dto)

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List[Entity]:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: EntityIdentity, **kwargs: ApplicationService) -> None:
        raise NotImplementedError
