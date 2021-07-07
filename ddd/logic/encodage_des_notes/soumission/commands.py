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
class NoteEtudiantCommand(interface.CommandRequest):
    noma = attr.ib(type=str)
    note = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class EncoderFeuilleDeNotesCommand(interface.CommandRequest):
    code_unite_enseignement = attr.ib(type=str)
    annee_unite_enseignement = attr.ib(type=int)
    numero_session = attr.ib(type=int)
    matricule_fgs_enseignant = attr.ib(type=str)
    notes_etudiants = attr.ib(type=List[NoteEtudiantCommand], default=[])


@attr.s(frozen=True, slots=True)
class SoumettreFeuilleDeNotesCommand(interface.CommandRequest):
    code_unite_enseignement = attr.ib(type=str)
    annee_unite_enseignement = attr.ib(type=int)
    numero_session = attr.ib(type=int)
    matricule_fgs_enseignant = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class AssignerResponsableDeNotesCommand(interface.CommandRequest):
    code_unite_enseignement = attr.ib(type=str)
    annee_unite_enseignement = attr.ib(type=int)
    matricule_fgs_enseignant = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class DesassignerResponsableDeNotesCommand(interface.CommandRequest):
    code_unite_enseignement = attr.ib(type=str)
    annee_unite_enseignement = attr.ib(type=int)
    matricule_fgs_enseignant = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetProgressionGeneraleCommand(interface.CommandRequest):
    matricule_fgs_enseignant = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetFeuilleDeNotesCommand(interface.CommandRequest):
    matricule_fgs_enseignant = attr.ib(type=str)
    code_unite_enseignement = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class SearchAdressesFeuilleDeNotesCommand(interface.CommandRequest):
    codes_unite_enseignement = attr.ib(type=List[str])
