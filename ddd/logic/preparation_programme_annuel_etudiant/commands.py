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


@attr.s(frozen=True, slots=True)
class GetFormulaireInscriptionCoursCommand(interface.CommandRequest):
    annee_formation = attr.ib(type=int)
    sigle_formation = attr.ib(type=str)
    version_formation = attr.ib(type=str)
    transition_formation = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class UniteEnseignementCommand(interface.CommandRequest):
    annee = attr.ib(type=int)
    code = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class AjouterUEAuProgrammeCommand(interface.CommandRequest):
    annee_formation = attr.ib(type=int)
    sigle_formation = attr.ib(type=str)
    version_formation = attr.ib(type=str)
    position_dans_programme = attr.ib(type=str)  # exemple : LDROI100B | LDROI110A | LDROI1001
    unites_enseignements = attr.ib(type=List[UniteEnseignementCommand])
