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

from osis_common.ddd import interface
from osis_common.ddd.interface import ApplicationService, RootEntity, EntityIdentity


class InMemoryGenericRepository(interface.AbstractRepository):
    entities = list()  # type: List[RootEntity]

    @classmethod
    def get(cls, entity_id: 'EntityIdentity') -> 'RootEntity':
        return next(
            (entity for entity in cls.entities if entity.entity_id == entity_id),
            None
        )

    @classmethod
    def search(cls, entity_ids: Optional[List['EntityIdentity']] = None, **kwargs) -> List['RootEntity']:
        return [entity for entity in cls.entities if entity.entity_id in entity_ids]

    @classmethod
    def delete(cls, entity_id: 'EntityIdentity', **kwargs: ApplicationService) -> None:
        cls.entities.remove(cls.get(entity_id))

    @classmethod
    def save(cls, entity: 'RootEntity') -> None:
        if entity in cls.entities:
            cls.entities.remove(entity)
        cls.entities.append(entity)

    @classmethod
    def get_all_identities(cls) -> List['EntityIdentity']:
        return [entity.entity_id for entity in cls.entities]
