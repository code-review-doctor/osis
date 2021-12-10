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
class ProgrammeInscriptionCoursIdentity(interface.EntityIdentity):
    annee_formation: int
    sigle_formation: str
    version_formation: str


@attr.s(slots=True, auto_attribs=True)
class ProgrammeInscriptionCours(interface.RootEntity):
    entity_id: ProgrammeInscriptionCoursIdentity
    ues: List['UniteEnseignement']
    groupements: List['Groupement']

    def ajouter_unite_enseignement(self, unite_enseignement: 'CodeUniteEnseignement', a_inclure_dans: 'CodeGroupement'):
        raise NotImplementedError


# à déplacer dans groupement.py
CodeGroupement = str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class GroupementIdentity(interface.EntityIdentity):
    code: CodeGroupement


@attr.s(slots=True, auto_attribs=True)
class Groupement(interface.Entity):
    inclus_dans: List['Groupement']


# à déplacer dans unite_enseignement.py
CodeUniteEnseignement = str


@attr.s(frozen=True, slots=True, auto_attribs=True)
class UniteEnseignementIdentity(interface.EntityIdentity):
    code: CodeUniteEnseignement


@attr.s(slots=True, auto_attribs=True)
class UniteEnseignement(interface.Entity):
    inclus_dans: List['Groupement']