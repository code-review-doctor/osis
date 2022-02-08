##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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

from ddd.logic.preparation_programme_annuel_etudiant.domain.model.groupement_ajuste_inscription_cours import \
    CodeUniteEnseignement
from osis_common.ddd import interface


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetFormulaireInscriptionCoursCommand(interface.CommandRequest):
    annee: int
    code_programme: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetUniteEnseignementCommand(interface.CommandRequest):
    code: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class AjouterUEAuProgrammeCommand(interface.CommandRequest):
    annee: int
    code_programme: str
    ajouter_dans: str  # code groupement
    unites_enseignements: List[CodeUniteEnseignement]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetProgrammeInscriptionCoursCommand(interface.CommandRequest):
    annee: int
    code_programme: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class RetirerUEDuProgrammeCommand(interface.CommandRequest):
    annee_formation: int
    sigle_formation: str
    version_formation: str
    transition_formation: str
    groupement_uuid: str  # TODO :: code groupement ou uuid groupement ?
    unites_enseignements: List[GetUniteEnseignementCommand]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetContenuGroupementCommand(interface.CommandRequest):
    code_formation: str
    code: str  # TODO :: code groupement ou uuid groupement ?
    annee: int


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ModifierUniteEnseignementCommand(interface.CommandRequest):
    code: str
    annee: int
    bloc: int


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ModifierUEDuGroupementCommand(interface.CommandRequest):
    annee_formation: int
    sigle_formation: str
    version_formation: str
    transition_formation: str
    a_ajuster_dans: str  # TODO :: code groupement ou uuid groupement ?
    unites_enseignements: List[ModifierUniteEnseignementCommand]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class AnnulerActionSurUEDuProgrammeCommand(interface.CommandRequest):
    annee_formation: int
    sigle_formation: str
    version_formation: str
    transition_formation: str
    a_annuler_dans: str  # TODO :: code groupement ou uuid groupement ?
    unite_enseignement: GetUniteEnseignementCommand


@attr.s(frozen=True, slots=True, auto_attribs=True)
class DeplacerVersLeHautUEAjouteeDansProgrammeCommand(interface.CommandRequest):
    annee_formation: int
    sigle_formation: str
    version_formation: str
    transition_formation: str
    ajoutee_dans: str  # TODO :: code groupement ou uuid groupement ?
    unite_enseignement: GetUniteEnseignementCommand


@attr.s(frozen=True, slots=True, auto_attribs=True)
class DeplacerVersLeBasUEAjouteeDansProgrammeCommand(interface.CommandRequest):
    annee_formation: int
    sigle_formation: str
    version_formation: str
    transition_formation: str
    ajoutee_dans: str  # TODO :: code groupement ou uuid groupement ?
    unite_enseignement: GetUniteEnseignementCommand


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetFormationCommand(interface.CommandRequest):
    annee: int
    code: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GetUnitesEnseignementContenuesCommand(interface.CommandRequest):
    code_programme: str
    annee: int
