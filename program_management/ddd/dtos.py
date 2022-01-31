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
from decimal import Decimal
from typing import List

import attr

from osis_common.ddd.interface import DTO


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementDTO(DTO):
    bloc: int
    code: str
    intitule_complet: str
    quadrimestre: str
    quadrimestre_texte: str
    credits_absolus: Decimal
    volume_annuel_pm: int
    volume_annuel_pp: int
    obligatoire: bool
    session_derogation: str
    credits_relatifs: int


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementDTO(DTO):
    code: str
    intitule: str
    obligatoire: bool
    remarque: str
    intitule_complet: str
    credits: Decimal


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ContenuNoeudDTO(DTO):
    groupement_contenant: GroupementDTO
    unites_enseignement_contenues: List['UniteEnseignementDTO']
    groupements_contenus: List['ContenuNoeudDTO']


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ProgrammeDeFormationDTO(DTO):
    racine: ContenuNoeudDTO
    annee: int
    sigle: str
    version: str
    code: str
    intitule_formation: str
