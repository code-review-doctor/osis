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

from base.models.entity_version import EntityVersion
from osis_common.ddd import interface
from osis_common.ddd.interface import EntityIdentity, ApplicationService, Entity, RootEntity
from ddd.logic.learning_unit.builder.responsible_entity_identity_builder import ResponsibleEntityIdentityBuilder
from workshops_ddd_ue.domain.responsible_entity import ResponsibleEntity, ResponsibleEntityIdentity


class EntityRepository(interface.AbstractRepository):
    @classmethod
    def save(cls, entity: RootEntity) -> None:
        raise NotImplementedError

    @classmethod
    def get(cls, entity_id: 'ResponsibleEntityIdentity') -> 'ResponsibleEntity':
        entity_version = EntityVersion.objects.get(acronym=entity_id.code)
        return ResponsibleEntity(
            entity_id=ResponsibleEntityIdentityBuilder.build_from_code(code=entity_version.acronym),
            type=entity_version.entity_type
        )  # FIXME :: reuse Builder instead

    @classmethod
    def search(cls, entity_ids: Optional[List[EntityIdentity]] = None, **kwargs) -> List[Entity]:
        raise NotImplementedError

    @classmethod
    def delete(cls, entity_id: EntityIdentity, **kwargs: ApplicationService) -> None:
        raise NotImplementedError
