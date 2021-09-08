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
    code_unite_enseignement = attr.ib(type=str, validator=attr.validators.instance_of(str))
    annee_unite_enseignement = attr.ib(type=int, validator=attr.validators.instance_of(int))
    numero_session = attr.ib(type=int, validator=attr.validators.instance_of(int))
    matricule_fgs_enseignant = attr.ib(type=str, validator=attr.validators.instance_of(str))
    noma_etudiant = attr.ib(type=str, validator=attr.validators.instance_of(str))
    email_etudiant = attr.ib(type=str, validator=attr.validators.instance_of(str))
    note = attr.ib(type=str, validator=attr.validators.instance_of(str))


@attr.s(frozen=True, slots=True)
class SoumettreNoteCommand(interface.CommandRequest):
    noma_etudiant = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class SoumettreNotesCommand(interface.CommandRequest):
    matricule_fgs_enseignant = attr.ib(type=str)
    code_unite_enseignement = attr.ib(type=str)
    annee_unite_enseignement = attr.ib(type=int)
    numero_session = attr.ib(type=int)
    notes = attr.ib(type=List[SoumettreNoteCommand])


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


@attr.s(frozen=True, slots=True)
class EncoderAdresseEntiteCommeAdresseFeuilleDeNotes(interface.CommandRequest):
    nom_cohorte = attr.ib(type=str)
    email = attr.ib(type=str)
    entite = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class EncoderAdresseFeuilleDeNotesSpecifique(interface.CommandRequest):
    nom_cohorte = attr.ib(type=str)
    email = attr.ib(type=str)
    destinataire = attr.ib(type=str)
    rue_numero = attr.ib(type=str)
    code_postal = attr.ib(type=str)
    ville = attr.ib(type=str)
    pays = attr.ib(type=str)
    telephone = attr.ib(type=str)
    fax = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class EcraserAdresseFeuilleDeNotesPremiereAnneeDeBachelier(interface.CommandRequest):
    nom_cohorte = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetAdresseFeuilleDeNotesServiceCommand(interface.CommandRequest):
    nom_cohorte = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetChoixEntitesAdresseFeuilleDeNotesCommand(interface.CommandRequest):
    nom_cohorte = attr.ib(type=str)


@attr.s(frozen=True, slots=True)
class GetResponsableDeNotesCommand(interface.CommandRequest):
    code_unite_enseignement = attr.ib(type=str)
    annee_unite_enseignement = attr.ib(type=int)
