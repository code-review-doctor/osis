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
from typing import Set

import attr

from ddd.logic.encodage_des_notes.soumission.domain.validator.exceptions import PasGestionnaireParcoursCohorteException
from osis_common.ddd import interface

Noma = str


@attr.s(frozen=True, slots=True)
class IdentiteGestionnaire(interface.EntityIdentity):
    matricule_fgs_gestionnaire = attr.ib(type=str)


@attr.s(slots=True)
class GestionnaireParcours(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteGestionnaire)
    cohortes_gerees = attr.ib(type=Set[str])

    def verifier_gere_cohorte(self, nom_cohorte) -> None:
        if nom_cohorte not in self.cohortes_gerees:
            raise PasGestionnaireParcoursCohorteException(nom_cohorte)
