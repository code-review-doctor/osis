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
from datetime import date

import attr

from ddd.logic.encodage_des_notes.encodage.domain.model._note import Note
from osis_common.ddd import interface

Noma = str


@attr.s(frozen=True, slots=True)
class IdentiteNoteEtudiant(interface.EntityIdentity):
    noma = attr.ib(type=Noma)
    code_unite_enseignement = attr.ib(type=str)
    annee_academique = attr.ib(type=int)
    numero_session = attr.ib(type=int)


@attr.s(slots=True)
class NoteEtudiant(interface.RootEntity):
    entity_id = attr.ib(type=IdentiteNoteEtudiant)
    email = attr.ib(type=str)
    note = attr.ib(type=Note)
    echeance_gestionnaire = attr.ib(type=date)
    nom_cohorte = attr.ib(type=str)
    note_decimale_autorisee = attr.ib(type=bool)

    @property
    def noma(self):
        return self.entity_id.noma

    @property
    def code_unite_enseignement(self):
        return self.entity_id.code_unite_enseignement

    @property
    def annee_academique(self):
        return self.entity_id.annee_academique

    @property
    def numero_session(self):
        return self.entity_id.numero_session

    @property
    def is_manquant(self) -> bool:
        return not bool(self.note.value)
