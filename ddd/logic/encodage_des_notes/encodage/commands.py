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
class EncoderNoteCommand(interface.CommandRequest):
    noma = attr.ib(type=str)
    email = attr.ib(type=str)
    code_unite_enseignement = attr.ib(type=str)
    note = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class EncoderNotesCommand(interface.CommandRequest):
    matricule_fgs_gestionnaire = attr.ib(type=str)
    notes_encodees = attr.ib(type=List[EncoderNoteCommand])


@attr.s(frozen=True, slots=True)
class GetFeuilleDeNotesGestionnaireCommand(interface.CommandRequest):
    matricule_fgs_gestionnaire = attr.ib(type=str)
    code_unite_enseignement = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetCohortesGestionnaireCommand(interface.CommandRequest):
    matricule_fgs_gestionnaire = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class SearchNotesCommand(interface.CommandRequest):
    noma = attr.ib(type=str)
    nom = attr.ib(type=str)
    prenom = attr.ib(type=str)
    etat = attr.ib(type=str)  # absence justifiee, injustifiee, tricherie, note manquante  TODO :: renommer ?
    nom_cohorte = attr.ib(type=str)
