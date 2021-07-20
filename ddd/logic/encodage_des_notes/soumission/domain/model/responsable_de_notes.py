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

from ddd.logic.encodage_des_notes.soumission.domain.model._unite_enseignement_identite import \
    UniteEnseignementIdentite, UniteEnseignementIdentiteBuilder
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True)
class IdentiteResponsableDeNotes(interface.EntityIdentity):
    matricule_fgs_enseignant = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class ResponsableDeNotes(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteResponsableDeNotes)
    unites_enseignements = attr.ib(type=Set[UniteEnseignementIdentite])

    def assigner(self, code_unite_enseignement: str, annee_academique: int) -> None:
        self.unites_enseignements.add(
            UniteEnseignementIdentiteBuilder.build_from_code_and_annee(code_unite_enseignement, annee_academique)
        )

    def desassigner(self, code_unite_enseignement: str, annee_academique: int) -> None:
        self.unites_enseignements.remove(
            UniteEnseignementIdentiteBuilder.build_from_code_and_annee(code_unite_enseignement, annee_academique)
        )

    def est_responsable_de(self, code_unite_enseignement: str, annee_academique: int) -> bool:
        unite_enseignement_identite = UniteEnseignementIdentiteBuilder.build_from_code_and_annee(
            code_unite_enseignement,
            annee_academique
        )
        return unite_enseignement_identite in self.unites_enseignements

    @property
    def matricule_fgs_enseignant(self) -> str:
        return self.entity_id.matricule_fgs_enseignant
