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

import attr

from osis_common.ddd import interface


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetFormulaireInscriptionCoursCommand(interface.CommandRequest):
    annee_formation: int
    sigle_formation: str
    version_formation: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementCommand(interface.CommandRequest):
    code: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class AjouterUEAuProgrammeCommand(interface.CommandRequest):
    annee_formation: int
    sigle_formation: str
    version_formation: str
    a_inclure_dans: str  # code groupement
    unites_enseignements: List[UniteEnseignementCommand]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetProgrammeInscriptionCoursServiceCommand(interface.CommandRequest):
    annee_formation: int
    sigle_formation: str
    version_formation: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class RetirerUEDuProgrammeCommand(interface.CommandRequest):
    annee_formation: int
    sigle_formation: str
    version_formation: str
    a_retirer_de: str  # code groupement
    unites_enseignements: List[UniteEnseignementCommand]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetContenuGroupementCommand(interface.CommandRequest):
    sigle_formation: str
    version_formation: str
    code: str
    annee: int
