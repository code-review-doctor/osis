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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import Optional

import attr

from base.models.enums.entity_type import EntityType
from ddd.logic.shared_kernel.entite.domain.model._adresse_entite import AdresseEntite
from osis_common.ddd import interface


@attr.s(slots=True, frozen=True)
class IdentiteEntite(interface.EntityIdentity):
    sigle = attr.ib(type=str)


@attr.s(slots=True)
class Entite(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteEntite)
    parent = attr.ib(type=Optional[IdentiteEntite])
    intitule = attr.ib(type=str)
    type = attr.ib(type=EntityType)
    adresse = attr.ib(type=AdresseEntite)

    @property
    def sigle(self) -> str:
        return self.entity_id.sigle

    @property
    def sigle_du_parent(self) -> str:
        return self.parent.sigle if self.parent else ""

    def est_faculte(self) -> bool:
        return self.type == EntityType.FACULTY
