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
from decimal import Decimal
from typing import List

import attr

from osis_common.ddd.interface import DTO


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementDTO(DTO):
    inclus_dans: 'GroupementDTO'
    bloc: int
    code: str
    intitule_complet: str
    quadrimestre: str
    credits_absolus: Decimal
    volume_annuel_pm: int
    volume_annuel_pp: int
    obligatoire: bool
    session_derogation: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementDTO(DTO):
    inclus_dans: List['GroupementDTO']
    intitule: str
    obligatoire: bool


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ContenuGroupementDTO(DTO):
    ues: List[UniteEnseignementDTO]
    groupement: GroupementDTO


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ProgrammeDTO(DTO):
    ues: List[UniteEnseignementDTO]
    groupements: List[GroupementDTO]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class FormulaireInscriptionCoursDTO(DTO):
    annee_formation: int
    sigle_formation: str
    version_formation: str
    intitule_complet_formation: str  # intitulé de la formation + version formation
    programme: ProgrammeDTO


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ProgrammeInscriptionCoursDTO(DTO):
    annee_formation: int
    sigle_formation: str
    version_formation: str
    intitule_complet_formation: str  # intitulé de la formation + version formation
    ues: List[UniteEnseignementDTO]
    groupements: List[GroupementDTO]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementCatalogueDTO(DTO):
    inclus_dans: 'GroupementCatalogueDTO'
    bloc: int
    code: str
    intitule_complet: str
    quadrimestre: str
    credits_absolus: Decimal
    volume_annuel_pm: int
    volume_annuel_pp: int


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementCatalogueDTO(DTO):
    # groupement provenant du catalogue (sans surcharge d'ajout, suppression ou modification)
    inclus_dans: 'GroupementCatalogueDTO'
    intitule: str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ProgrammeDetailleDTO(DTO):
    unites_enseignement: List[UniteEnseignementCatalogueDTO]
    groupements: List[GroupementCatalogueDTO]


@attr.s(frozen=True, slots=True, auto_attribs=True)
class FormationDTO(DTO):
    programme_detaille: ProgrammeDetailleDTO
    annee: int
    sigle: str
    version: str
    intitule_complet: str  # intitulé de la formation + version formation
