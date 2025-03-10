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


EntityCode = str


@attr.s(frozen=True, slots=True)
class UCLEntityIdentity(interface.EntityIdentity):
    code = attr.ib(type=EntityCode)


@attr.s(slots=True, hash=False, eq=False)
class UclEntity(interface.RootEntity):
    entity_id = attr.ib(type=UCLEntityIdentity)
    type = attr.ib(type=EntityType)

    @property
    def code(self) -> EntityCode:
        return self.entity_id.code

    def is_responsible_entity(self) -> bool:
        authorized_types = [
            EntityType.SECTOR,
            EntityType.FACULTY,
            EntityType.SCHOOL,
            EntityType.DOCTORAL_COMMISSION,
        ]
        authorized_codes = [
            "ILV",
            "IUFC",
            "CCR",
            "LLL",
        ]
        if not(self.type in authorized_types or self.code in authorized_codes):
            return False
        return True
