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
import attr

from base.models.enums.entity_type import EntityType
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class ResponsibleEntityIdentity(interface.EntityIdentity):
    code = attr.ib(type=str)


@attr.s(slots=True, hash=False, eq=False)
class ResponsibleEntity(interface.RootEntity):
    entity_id = attr.ib(type=ResponsibleEntityIdentity)
    type = attr.ib(type=EntityType)

    @property
    def code(self) -> str:
        return self.entity_id.code

    def is_sector(self):
        return self.type == EntityType.SECTOR

    def is_faculty(self):
        return self.type == EntityType.FACULTY

    def is_school(self):
        return self.type == EntityType.SCHOOL

    def is_doctoral_commission(self):
        return self.type == EntityType.DOCTORAL_COMMISSION
