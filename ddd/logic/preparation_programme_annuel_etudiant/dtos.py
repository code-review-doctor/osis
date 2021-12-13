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
from collections import namedtuple
from decimal import Decimal
from typing import Optional, List

import attr

from osis_common.ddd.interface import DTO


@attr.s(frozen=True, slots=True)
class UniteEnseignementDTO(DTO):
    inclus_dans = attr.ib(type='GroupementDTO')
    bloc = attr.ib(type=int)
    code = attr.ib(type=str)
    intitule_complet = attr.ib(type=str)
    quadrimestre = attr.ib(type=str)
    credits_absolus = attr.ib(type=Decimal)
    volume_annuel_pm = attr.ib(type=int)
    volume_annuel_pp = attr.ib(type=int)


@attr.s(frozen=True, slots=True)
class GroupementDTO(DTO):
    inclus_dans = attr.ib(type='GroupementDTO')
    intitule = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class ProgrammeDTO(DTO):
    ues = attr.ib(type=List[UniteEnseignementDTO])
    groupements = attr.ib(type=List[GroupementDTO])


@attr.s(frozen=True, slots=True)
class FormulaireInscriptionCoursDTO(DTO):
    annee_formation = attr.ib(type=int)
    sigle_formation = attr.ib(type=str)
    version_formation = attr.ib(type=str)
    intitule_complet_formation = attr.ib(type=str)  # intitulé de la formation + version formation
    programme = attr.ib(type=ProgrammeDTO)


@attr.s(frozen=True, slots=True)
class UniteEnseignementCatalogueDTO(DTO):
    inclus_dans = attr.ib(type='GroupementCatalogueDTO')
    bloc = attr.ib(type=int)
    code = attr.ib(type=str)
    intitule_complet = attr.ib(type=str)
    quadrimestre = attr.ib(type=str)
    credits_absolus = attr.ib(type=Decimal)
    volume_annuel_pm = attr.ib(type=int)
    volume_annuel_pp = attr.ib(type=int)
    obligatoire = attr.ib(type=bool)
    detail = attr.ib(type=str)  # TODO : doute sur le mot détail ça comprends plusieurs infos.
    # Exemple :   LCOPS1124 Philosophie [30h + 0h] (5 crédits)


@attr.s(frozen=True, slots=True)
class GroupementCatalogueDTO(DTO):
    inclus_dans = attr.ib(type='GroupementCatalogueDTO')
    intitule = attr.ib(type=str)
    obligatoire = attr.ib(type=bool)
    remarque = attr.ib(type=str)
    commentaire = attr.ib(type=str)
    detail = attr.ib(type=str)  # TODO : doute sur le mot détail ça comprends plusieurs infos.
    # Exemple : Programme de base (150 crédits)


@attr.s(frozen=True, slots=True)
class ProgrammeDetailleDTO(DTO):
    unites_enseignement = attr.ib(type=List[UniteEnseignementCatalogueDTO])
    groupements = attr.ib(type=List[GroupementCatalogueDTO])


@attr.s(frozen=True, slots=True)
class FormationDTO(DTO):
    programme_detaille = attr.ib(type=ProgrammeDetailleDTO)
    annee = attr.ib(type=int)
    sigle = attr.ib(type=str)
    version = attr.ib(type=str)
    intitule_complet = attr.ib(type=str)  # intitulé de la formation + version formation
